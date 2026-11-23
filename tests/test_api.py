import json
from pathlib import Path
import pytest
from backend import create_app


def _generate(client, payload):
    response = client.post('/api/v1/runs', json=payload)
    assert response.status_code == 201, response.json
    return response.json['record']


def _rubric(score=4):
    return {key:{'score':score,'justification':'A resposta informa o próximo passo do atendimento.'}
            for key in ('clarity','customer_fit','actionability')}


def test_catalog_health_meta(client):
    assert client.get('/api/v1/health').json['status'] == 'ok'
    assert client.get('/api/v1/meta').json['is_demo'] is True
    assert len(client.get('/api/v1/profiles').json) == 4
    assert len(client.get('/api/v1/tickets').json) >= 3
    assert client.get('/').status_code == 200
    assert client.get('/style.css').status_code == 200


def test_generation_cache_export_and_history(client, payload, app):
    first = client.post('/api/v1/runs',json=payload)
    assert first.status_code == 201
    second = client.post('/api/v1/runs',json=payload)
    assert second.status_code == 200
    assert second.json['cached'] is True
    assert first.json['record']['id'] == second.json['record']['id']
    assert len(client.get('/api/v1/runs').json) == 1
    assert first.json['record']['settings']['temperature'] == 0.2
    exported = client.get('/api/v1/runs/1/export')
    assert exported.status_code == 200
    assert json.loads(exported.data)['prompt_version'] == 'v1'
    assert (Path(app.config['EXPORT_DIR'])/'generation_1.json').is_file()


@pytest.mark.parametrize('type_,key',[
    ('diagnosis','hypotheses'),('resolution','steps'),
    ('questions','questions'),('flowchart','ascii_flow')
])
def test_four_content_types(client,payload,type_,key):
    record = _generate(client,{**payload,'content_type':type_})
    assert key in record['output']


def test_experiment_keeps_context_and_changes_prompt(client,payload):
    response = client.post('/api/v1/experiments',json=payload)
    assert response.status_code == 200
    a,b=[value['record'] for value in response.json['runs']]
    assert [a['prompt_version'],b['prompt_version']] == ['v1','v2']
    assert a['scenario_key'] == b['scenario_key']
    assert a['prompt_hash'] != b['prompt_hash']
    assert a['settings'] == b['settings']
    assert a['model'] == b['model']
    assert a['provider'] == b['provider']
    second=client.post('/api/v1/experiments',json=payload)
    assert all(value['cached'] for value in second.json['runs'])


@pytest.mark.parametrize('invalid',[
    {}, {'customer_id':'unknown','ticket':'erro','content_type':'diagnosis'},
    {'customer_id':'c1','ticket':'','content_type':'diagnosis'},
    {'customer_id':'c1','ticket':'teste','content_type':'anything'},
    {'customer_id':'c1','ticket':'teste','content_type':'diagnosis','prompt_version':'v42'},
    {'customer_id':'c1','ticket':'x'*5001,'content_type':'diagnosis'},
])
def test_invalid_inputs(client,invalid):
    assert client.post('/api/v1/runs',json=invalid).status_code == 400


def test_invalid_json_and_unknown(client):
    response=client.post('/api/v1/runs', data='garbage', content_type='application/json')
    assert response.status_code == 400
    assert client.get('/api/v1/runs/555').status_code == 404
    assert client.get('/api/v1/comparisons/555').status_code == 404


def test_rubric_and_comparison_persist(client,payload,app):
    entries=client.post('/api/v1/experiments',json=payload).json['runs']
    ids=[item['record']['id'] for item in entries]
    body={'generation_ids': ids}
    assert client.post('/api/v1/comparisons',json=body).status_code == 400
    for i,score in zip(ids,[3,5]):
        res=client.put(f'/api/v1/runs/{i}/evaluation',json=_rubric(score))
        assert res.status_code == 200
    result=client.post('/api/v1/comparisons',json=body)
    assert result.status_code == 200
    record=result.json
    assert record['summary']['v1_average'] == 3
    assert record['summary']['v2_average'] == 5
    assert record['summary']['delta_v2_minus_v1'] == 2
    assert record['summary']['higher_scored_version'] == 'v2'
    assert len(record['results']) == 2
    assert len(client.get('/api/v1/comparisons').json) == 1
    assert client.get(f"/api/v1/comparisons/{record['id']}").json['results'][0]['evaluation']
    exported=client.get(f"/api/v1/comparisons/{record['id']}/export")
    assert json.loads(exported.data)['summary']['v2_average'] == 5
    path=Path(app.config['EXPORT_DIR']) / f"comparison_{record['id']}.json"
    assert path.is_file()
    # Uma comparação repetida da mesma dupla atualiza o registro, não duplica.
    assert client.post('/api/v1/comparisons',json=body).json['id'] == record['id']
    assert len(client.get('/api/v1/comparisons').json) == 1


def test_comparison_rejects_different_tickets_or_duplicate_versions(client,payload):
    a=_generate(client,payload)
    b=_generate(client,{**payload,'ticket':'Outro sintoma','prompt_version':'v2'})
    for item in (a,b):
        client.put(f"/api/v1/runs/{item['id']}/evaluation",json=_rubric())
    assert client.post('/api/v1/comparisons',json={'generation_ids':[a['id'],b['id']]}).status_code == 400
    assert client.post('/api/v1/comparisons',json={'generation_ids':[a['id'],a['id']]}).status_code == 400


def test_comparison_rejects_different_model_settings(client,payload,app):
    first=_generate(client,payload)
    app.config['AI_TEMPERATURE']=0.6
    second=_generate(client,{**payload,'prompt_version':'v2'})
    for item in (first,second):
        client.put(f"/api/v1/runs/{item['id']}/evaluation",json=_rubric())
    assert client.post('/api/v1/comparisons',json={'generation_ids':[first['id'],second['id']]}).status_code == 400


def test_rubric_validation(client,payload):
    record=_generate(client,payload)
    url=f"/api/v1/runs/{record['id']}/evaluation"
    assert client.put(url,json={'clarity':{'score':5}}).status_code == 400
    assert client.put(url,json=_rubric(6)).status_code == 400
    assert client.put(url,json=_rubric(True)).status_code == 400
    bad=_rubric();bad['clarity']['justification']='a'
    assert client.put(url,json=bad).status_code == 400
    assert client.put('/api/v1/runs/777/evaluation',json=_rubric()).status_code == 404


def test_access_token_protection(tmp_path,payload):
    app=create_app({'TESTING':True,'APP_ENV':'production','APP_ACCESS_TOKEN':'private-key',
                    'AI_PROVIDER':'demo','AI_MODEL':'demo-local',
                    'SQLALCHEMY_DATABASE_URI':f"sqlite:///{tmp_path/'secured.db'}",
                    'EXPORT_DIR':str(tmp_path/'history')})
    client=app.test_client()
    assert client.get('/api/v1/health').status_code == 200
    assert client.get('/api/v1/profiles').status_code == 401
    assert client.post('/api/v1/runs',json=payload).status_code == 401
    headers={'X-Access-Token':'private-key'}
    assert client.get('/api/v1/profiles',headers=headers).status_code == 200
    assert client.post('/api/v1/runs',json=payload,headers=headers).status_code == 201


def test_production_requires_access_token(tmp_path):
    with pytest.raises(RuntimeError,match='APP_ACCESS_TOKEN'):
        create_app({'APP_ENV':'production','APP_ACCESS_TOKEN':'',
                    'SQLALCHEMY_DATABASE_URI':f"sqlite:///{tmp_path/'invalid.db'}"})


def test_export_allows_re_evaluation_with_download_response_alive(client, payload):
    """O download não pode bloquear a substituição do JSON no Windows."""
    record = _generate(client, payload)
    run_id = record["id"]
    url = f"/api/v1/runs/{run_id}/evaluation"
    assert client.put(url, json=_rubric(3)).status_code == 200

    downloaded = client.get(f"/api/v1/runs/{run_id}/export")
    assert downloaded.status_code == 200
    assert downloaded.headers["Content-Disposition"].startswith("attachment;")
    assert json.loads(downloaded.data)["evaluation"]["clarity"]["score"] == 3

    # Mantém downloaded vivo para reproduzir o cenário de handle pendente.
    assert client.put(url, json=_rubric(5)).status_code == 200
    updated = client.get(f"/api/v1/runs/{run_id}/export")
    assert json.loads(updated.data)["evaluation"]["clarity"]["score"] == 5
