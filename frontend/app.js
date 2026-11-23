'use strict';

const $ = (id) => document.getElementById(id);
const labels = {diagnosis:'Diagnóstico',resolution:'Resolução',questions:'Perguntas',flowchart:'Fluxograma'};
const criteria = [
  ['clarity','Clareza'], ['customer_fit','Adequação ao cliente'], ['actionability','Acionabilidade']
];
const state = {tickets: [], pair: [], apiToken: '', busy: false};

function showMessage(message, error = false) {
  const target = $('flash');
  target.hidden = false;
  target.className = 'flash' + (error ? ' error' : '');
  target.textContent = message;
}

async function api(path, options = {}) {
  const headers = {...(options.body ? {'Content-Type':'application/json'} : {}), ...(state.apiToken ? {'X-Access-Token':state.apiToken} : {})};
  const response = await fetch('/api/v1' + path, {...options, headers});
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `Falha HTTP ${response.status}`);
  return data;
}

function option(select, value, description) {
  const item = document.createElement('option');
  item.value = value;
  item.textContent = description;
  select.append(item);
}

function node(tag, className, content) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (content !== undefined) item.textContent = content;
  return item;
}

function formPayload() {
  return {customer_id:$('customer').value, ticket:$('ticket').value.trim(),
          content_type:$('contentType').value, prompt_version:$('promptVersion').value};
}

function setBusy(busy) {
  state.busy = busy;
  $('generateButton').disabled = busy;
  $('experimentButton').disabled = busy;
  $('generateButton').textContent = busy ? 'Executando…' : 'Gerar resposta →';
  $('experimentButton').textContent = busy ? 'Aguarde…' : 'Comparar v1 e v2';
}

function renderResults(records, flags = []) {
  const grid = $('resultsGrid'); grid.replaceChildren();
  records.forEach((record, i) => {
    const outer = node('article','result-card');
    const head = node('div','result-head');
    head.append(node('strong','',`#${record.id} · ${record.prompt_version} · ${labels[record.content_type]}`));
    head.append(node('span','pill '+(flags[i] ? 'soft' : ''), flags[i] ? 'CACHE' : 'SALVO'));
    const meta = node('div','result-meta');
    meta.append(node('span','',`${record.provider} / ${record.model}`));
    meta.append(node('span','',record.timestamp));
    const pre = node('pre','',JSON.stringify(record.output,null,2));
    const actions = node('div','result-actions');
    const download = node('button','btn btn-quiet btn-small','Baixar JSON');
    download.type = 'button';
    download.addEventListener('click', () => downloadFile(`/runs/${record.id}/export`, `generation_${record.id}.json`));
    actions.append(download);
    outer.append(head,meta,pre,actions);
    grid.append(outer);
  });
}

async function downloadFile(path, filename) {
  try {
    const response = await fetch('/api/v1' + path, {headers:state.apiToken ? {'X-Access-Token':state.apiToken} : {}});
    if (!response.ok) throw new Error('Não foi possível exportar o JSON.');
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = node('a','');link.href = url; link.download = filename;
    document.body.append(link); link.click(); link.remove(); URL.revokeObjectURL(url);
  } catch(error) { showMessage(error.message,true); }
}

function renderReviews(records) {
  state.pair = records;
  const grid = $('reviewGrid'); grid.replaceChildren();
  $('comparisonSummary').hidden = true;
  $('saveComparison').disabled = records.length !== 2 || records.some(r => !r.evaluation);
  $('reviewNote').textContent = records.length === 2 ? 'Duas avaliações são necessárias para salvar a comparação.' : 'Avalie esta execução; para comparar, selecione duas versões.';
  records.forEach(record => {
    const card = node('article','review-card');
    const header = node('h3','',`${record.prompt_version} · Execução #${record.id}`);
    const form = node('form','');
    form.dataset.id = record.id;
    criteria.forEach(([key,label]) => {
      const field = node('label','',label);
      const row = node('div','rubric-row');
      const select = node('select','');
      select.name = `${key}_score`;
      for (let score = 1;score <= 5;score++) option(select,score,String(score));
      select.value = record.evaluation?.[key]?.score ?? '3';
      const justification = node('textarea','');
      justification.name = `${key}_justification`;
      justification.placeholder = 'Justifique a nota com base na resposta.';
      justification.minLength = 5; justification.maxLength = 400;
      justification.value = record.evaluation?.[key]?.justification ?? '';
      justification.required = true;
      row.append(select,justification);field.append(row);form.append(field);
    });
    const save = node('button','btn btn-outline','Salvar avaliação');save.type = 'submit';
    form.append(save);
    if (record.evaluation) form.append(node('div','saved','✓ Avaliação registrada'));
    form.addEventListener('submit',async (event) => {
      event.preventDefault();
      const data = new FormData(form); const rubric = {};
      criteria.forEach(([key]) => rubric[key] = {score:Number(data.get(`${key}_score`)),justification:String(data.get(`${key}_justification`)).trim()});
      try {
        const updated = await api(`/runs/${record.id}/evaluation`,{method:'PUT',body:JSON.stringify(rubric)});
        const index = state.pair.findIndex(item => item.id === record.id);
        state.pair[index] = updated;
        renderReviews([...state.pair]);
        await refreshHistory();
        showMessage(`Avaliação #${record.id} salva. Agora registre a comparação, se houver duas versões.`);
      } catch(error) { showMessage(error.message,true); }
    });
    card.append(header,form);grid.append(card);
  });
}

function renderComparison(comparison) {
  const container = $('comparisonSummary'); container.hidden = false;
  container.className = 'summary'; container.replaceChildren();
  container.append(node('h3','',`Comparação #${comparison.id} salva`));
  const metrics = node('div','summary-grid');
  const entries = [['Média v1',comparison.summary.v1_average],['Média v2',comparison.summary.v2_average],['Variação v2 - v1',comparison.summary.delta_v2_minus_v1]];
  entries.forEach(([label,value]) => {const box=node('div','metric');box.append(node('small','',label),node('strong','',String(value)));metrics.append(box);});
  container.append(metrics);
  container.append(node('p','section-help',comparison.summary.disclaimer));
  const button = node('button','btn btn-outline btn-small','Exportar comparação JSON');
  button.addEventListener('click',()=>downloadFile(`/comparisons/${comparison.id}/export`,`comparison_${comparison.id}.json`));
  container.append(button);
}

async function generate(experiment = false) {
  if (state.busy) return;
  try {
    setBusy(true);
    const path = experiment ? '/experiments' : '/runs';
    const result = await api(path,{method:'POST',body:JSON.stringify(formPayload())});
    const runs = experiment ? result.runs.map(r => r.record) : [result.record];
    const hits = experiment ? result.runs.map(r => r.cached) : [result.cached];
    renderResults(runs,hits);
    renderReviews(runs);
    await refreshHistory();
    showMessage(experiment ? 'Duas versões geradas com o mesmo cenário. Avalie cada uma antes de concluir.' : (result.cached ? 'Resposta recuperada do cache.' : 'Resposta gerada e salva.'));
    $('results').scrollIntoView({behavior:'smooth',block:'start'});
  } catch(error) { showMessage(error.message,true); }
  finally { setBusy(false); }
}

async function refreshHistory() {
  const [runs,comparisons] = await Promise.all([api('/runs'),api('/comparisons')]);
  const runList = $('historyRuns');const comparisonList = $('historyComparisons');
  runList.replaceChildren();comparisonList.replaceChildren();
  runs.forEach(run => {
    const row = node('div','history-item');const details = node('div','');
    details.append(node('strong','',`#${run.id} · ${run.prompt_version} · ${labels[run.content_type]}`));
    details.append(node('small','',`${run.customer_id} · ${run.evaluation ? 'Avaliado' : 'Pendente'} · ${run.provider}`));
    const actions = node('div','history-actions');
    const open = node('button','btn btn-quiet btn-small','Abrir');
    open.addEventListener('click',()=>{renderResults([run]);renderReviews([run]);$('results').scrollIntoView({behavior:'smooth'});});
    actions.append(open);row.append(details,actions);runList.append(row);
  });
  comparisons.forEach(compare => {
    const row = node('div','history-item');const details = node('div','');
    details.append(node('strong','',`Comparação #${compare.id}`));
    details.append(node('small','',`${compare.generation_ids.join(' × ')} · ${compare.timestamp}`));
    const open = node('button','btn btn-quiet btn-small','Abrir');
    open.addEventListener('click',async()=>{
      try {const full=await api(`/comparisons/${compare.id}`);renderResults(full.results);renderReviews(full.results);renderComparison(full);$('results').scrollIntoView({behavior:'smooth'});} catch(error){showMessage(error.message,true);}
    });
    row.append(details,open);comparisonList.append(row);
  });
  if (!runs.length) runList.append(node('p','hint','Nenhuma execução.'));
  if (!comparisons.length) comparisonList.append(node('p','hint','Nenhuma comparação avaliada.'));
}

async function initialize() {
  try {
    const [meta, profiles, tickets] = await Promise.all([api('/meta'),api('/profiles'),api('/tickets')]);
    state.tickets = tickets;
    $('providerBadge').textContent = `${meta.provider} / ${meta.model}`;
    $('providerNote').textContent = meta.is_demo
      ? 'Modo demonstração: resultados simulados. Não são evidência de avaliação de uma LLM.'
      : 'Modo API real. Cada geração nova pode gerar consumo na conta do provedor.';
    $('apiStatus').textContent = 'API disponível';
    $('customer').replaceChildren();$('ticketSelect').replaceChildren();
    profiles.forEach(profile => option($('customer'),profile.id,`${profile.name} · ${profile.technical_level} / ${profile.channel}`));
    tickets.forEach(ticket => option($('ticketSelect'),ticket.id,ticket.title));
    $('ticketSelect').dispatchEvent(new Event('change'));
    await refreshHistory();
  } catch(error) {
    $('apiStatus').textContent = 'Verifique a conexão';
    showMessage(`${error.message}. Se o servidor estiver protegido, informe o token e clique em Conectar.`,true);
  }
}

$('generator').addEventListener('submit',e => {e.preventDefault();generate(false);});
$('experimentButton').addEventListener('click',()=>generate(true));
$('ticketSelect').addEventListener('change',()=>{
  const t=state.tickets.find(item => item.id === $('ticketSelect').value);
  if (t) $('ticket').value = t.description;
});
$('retryAccess').addEventListener('click',()=>{state.apiToken = $('accessToken').value;initialize();});
$('refreshHistory').addEventListener('click',()=>refreshHistory().catch(error=>showMessage(error.message,true)));
$('saveComparison').addEventListener('click', async () => {
  if (state.pair.length !== 2 || state.pair.some(run=>!run.evaluation)) return;
  try {
    const data=await api('/comparisons',{method:'POST',body:JSON.stringify({generation_ids:state.pair.map(r=>r.id)})});
    renderComparison(data);await refreshHistory();showMessage(`Comparação #${data.id} registrada e exportada em JSON.`);
  } catch(error) {showMessage(error.message,true);}
});
initialize();
