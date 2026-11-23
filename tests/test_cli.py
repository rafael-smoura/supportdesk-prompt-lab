import json
from main import main


def test_cli_compare_in_demo(monkeypatch,app,capsys):
    monkeypatch.setattr('main.create_app',lambda:app)
    assert main(['--customer','c1','--ticket','t1','--compare']) == 0
    printed=capsys.readouterr().out
    assert '"prompt_version": "v1"' in printed
    assert '"prompt_version": "v2"' in printed


def test_cli_compare_with_evaluations(monkeypatch,app,capsys,tmp_path):
    monkeypatch.setattr('main.create_app',lambda:app)
    content={version:{key:{'score':3,'justification':'A resposta é objetiva e pode ser avaliada.'}
                      for key in ['clarity','customer_fit','actionability']}
             for version in ['v1','v2']}
    evaluation=tmp_path/'scores.json';evaluation.write_text(json.dumps(content),encoding='utf-8')
    assert main(['--compare','--evaluations',str(evaluation)]) == 0
    assert 'comparison' in capsys.readouterr().out
