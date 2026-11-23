import json
import pytest
import requests
from backend.providers.base import ProviderError
from backend.providers.http import GeminiProvider, OpenAICompatibleProvider
from backend.providers.factory import create_provider
from backend.services.catalog import find_profile
from backend.services.prompts import build_messages
from backend.services.rubric import average, validate_rubric
from backend.services.validators import validate_output


class FakeResponse:
    def __init__(self, body, status=200):
        self.body=body; self.status_code=status; self.ok=200 <= status < 300
        self.content=json.dumps(body).encode()
    def json(self):
        return self.body


class FakeSession:
    def __init__(self,response):self.response=response;self.calls=[]
    def post(self,*args,**kwargs):self.calls.append((args,kwargs));return self.response


def _cfg():
    return {'AI_MODEL':'gemini-2.5-flash-lite','AI_API_KEY':'test-key','AI_TEMPERATURE':0.2,
            'AI_MAX_TOKENS':1300,'AI_JSON_MODE':True,'AI_TIMEOUT':5,
            'AI_API_URL':'https://api.example.com/v1/chat/completions','AI_PROVIDER':'gemini'}


def _messages():
    return build_messages(find_profile('c1'),'O portal falhou','diagnosis','v2')


def test_prompts_versions_are_distinct_and_contextual():
    profile=find_profile('c1')
    v1=build_messages(profile,'Erro 403 ao acessar portal','diagnosis','v1')
    v2=build_messages(profile,'Erro 403 ao acessar portal','diagnosis','v2')
    assert v1 != v2
    assert 'Erro 403' in v2[1]['content']
    assert 'leigo' in v2[1]['content']
    assert 'Separe fatos' in v2[0]['content']
    assert 'senhas' in v2[0]['content']
    assert 'JSON' in v1[0]['content']


@pytest.mark.parametrize('type_,field',[
    ('diagnosis','hypotheses'),('resolution','steps'),('questions','questions'),('flowchart','ascii_flow')
])
def test_four_prompts_distinct(type_,field):
    built=build_messages(find_profile('c2'),'O sistema retornou erro',type_,'v2')
    assert field in built[0]['content']


def test_output_validation_rejects_extra_and_wrong_structure():
    with pytest.raises(ValueError):
        validate_output('diagnosis',{'hypotheses':[],'extra':'x'})
    with pytest.raises(ValueError):
        validate_output('questions',{'questions':[{'priority':2,'question':'x','reason':'y'}]})
    with pytest.raises(ValueError):
        validate_output('resolution',{'steps':[{'number':True,'action':'x','check':'y'}],'escalation':'x'})


def test_openai_adapter_request():
    body={'choices':[{'message':{'content':'{"foo": "bar"}'}}]}
    session=FakeSession(FakeResponse(body));config=_cfg();config['AI_PROVIDER']='openai_compatible'
    provider=OpenAICompatibleProvider(config,session)
    assert provider.generate(_messages(),'diagnosis') == {'foo':'bar'}
    args,kwargs=session.calls[0]
    assert args[0] == config['AI_API_URL']
    assert kwargs['json']['response_format'] == {'type':'json_object'}
    assert kwargs['headers']['Authorization'] == 'Bearer test-key'


def test_gemini_adapter_request():
    body={'candidates':[{'content':{'parts':[{'text':'{"a": 1}' }]}}]}
    session=FakeSession(FakeResponse(body));provider=GeminiProvider(_cfg(),session)
    assert provider.generate(_messages(),'diagnosis') == {'a':1}
    args,kwargs=session.calls[0]
    assert args[0].endswith('/gemini-2.5-flash-lite:generateContent')
    assert kwargs['headers']['x-goog-api-key'] == 'test-key'
    assert kwargs['json']['generationConfig']['responseMimeType'] == 'application/json'


@pytest.mark.parametrize('status,expected',[(429,429),(401,502),(500,502)])
def test_error_status_sanitized(status,expected):
    session=FakeSession(FakeResponse({'error':{'message':'secret-provider-error'}},status))
    with pytest.raises(ProviderError) as captured:
        GeminiProvider(_cfg(),session).generate(_messages(),'diagnosis')
    assert captured.value.status_code == expected
    assert 'secret-provider-error' not in str(captured.value)


def test_api_timeout():
    class TimeoutSession:
        def post(self,*args,**kwargs):raise requests.Timeout('long stack')
    with pytest.raises(ProviderError,match='Tempo') as exc:
        GeminiProvider(_cfg(),TimeoutSession()).generate(_messages(),'diagnosis')
    assert exc.value.status_code == 504


def test_provider_factory_requires_credentials():
    config=_cfg();config['AI_API_KEY']=''
    with pytest.raises(ProviderError,match='AI_API_KEY'):
        create_provider(config)
    config['AI_PROVIDER']='demo'
    assert create_provider(config).__class__.__name__ == 'DemoProvider'


def test_rubric_average():
    evaluation={key:{'score':score,'justification':'Justificativa suficientemente longa'}
                for key,score in [('clarity',5),('customer_fit',4),('actionability',3)]}
    assert average(validate_rubric(evaluation)) == 4
