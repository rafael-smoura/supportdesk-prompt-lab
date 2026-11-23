'use strict';

const byId = (id) => document.getElementById(id);
const typeLabels = {
  diagnosis: 'Diagnóstico', resolution: 'Resolução',
  questions: 'Perguntas', flowchart: 'Fluxograma'
};
const rubricCriteria = [
  ['clarity', 'Clareza', 'A resposta é compreensível e evita ambiguidades?'],
  ['customer_fit', 'Adequação ao cliente', 'A linguagem combina com o nível técnico do perfil?'],
  ['actionability', 'Acionabilidade', 'A resposta deixa claro o que fazer a seguir?']
];
const state = {
  profiles: [], tickets: [], runs: [], comparisons: [], selectedRuns: [],
  token: '', busy: false, isDemo: true
};

function element(tag, className, content) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (content !== undefined) item.textContent = String(content);
  return item;
}

function button(label, className, onClick) {
  const item = element('button', `button ${className}`, label);
  item.type = 'button';
  item.addEventListener('click', onClick);
  return item;
}

function message(value, error = false) {
  const banner = byId('flash');
  banner.textContent = value;
  banner.className = error ? 'flash error' : 'flash';
  banner.hidden = false;
}

function formattedDate(value) {
  const timestamp = new Date(value);
  return Number.isNaN(timestamp.getTime()) ? String(value) : new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short', timeStyle: 'short'
  }).format(timestamp);
}

async function request(path, options = {}) {
  const headers = { ...(options.body ? {'Content-Type': 'application/json'} : {}) };
  if (state.token) headers['X-Access-Token'] = state.token;
  const response = await fetch('/api/v1' + path, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401) byId('accessPanel').open = true;
    throw new Error(payload.error || `Não foi possível concluir a requisição (HTTP ${response.status}).`);
  }
  return payload;
}

async function download(path, filename) {
  try {
    const headers = state.token ? {'X-Access-Token': state.token} : {};
    const response = await fetch('/api/v1' + path, { headers });
    if (!response.ok) throw new Error('Não foi possível baixar o arquivo JSON.');
    const file = await response.blob();
    const url = URL.createObjectURL(file);
    const link = element('a');
    link.href = url;
    link.download = filename;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
  } catch (error) {
    message(error.message, true);
  }
}

function clearWithEmpty(target, heading, detail) {
  const wrap = element('div', 'empty-state compact-empty');
  wrap.append(element('strong', '', heading), element('p', '', detail));
  target.replaceChildren(wrap);
}

function fieldOption(select, value, title) {
  const option = element('option', '', title);
  option.value = value;
  select.append(option);
}

function showProfile() {
  const profile = state.profiles.find((item) => item.id === byId('customer').value);
  byId('profileInfo').textContent = profile
    ? `${profile.name} · Nível ${profile.technical_level} · Estilo ${profile.communication_style} · Atendimento por ${profile.channel}`
    : 'Escolha um perfil para ver seu contexto.';
}

function showTicket() {
  const ticket = state.tickets.find((item) => item.id === byId('ticketSelect').value);
  if (ticket) byId('ticket').value = ticket.description;
}

function currentPayload() {
  return {
    customer_id: byId('customer').value,
    ticket: byId('ticket').value.trim(),
    content_type: byId('contentType').value,
    prompt_version: byId('promptVersion').value
  };
}

function setBusy(value) {
  state.busy = value;
  for (const id of ['generateButton', 'experimentButton']) byId(id).disabled = value;
  byId('generateButton').textContent = value ? 'Gerando resposta…' : 'Gerar resposta ↗';
  byId('experimentButton').textContent = value ? 'Executando comparação…' : 'Comparar v1 × v2';
}

function outputSection(title, content) {
  const section = element('section', 'output-section');
  section.append(element('h4', '', title));
  if (Array.isArray(content)) {
    const list = element('ul');
    for (const item of content) {
      if (typeof item === 'string') list.append(element('li', '', item));
      else {
        const listItem = element('li');
        if (item.question) {
          listItem.append(element('strong', '', `${item.priority}. ${item.question}`));
          listItem.append(element('p', '', item.reason));
        } else if (item.action) {
          listItem.append(element('strong', '', `${item.number}. ${item.action}`));
          listItem.append(element('p', '', `Como verificar: ${item.check}`));
        }
        list.append(listItem);
      }
    }
    section.append(list);
  } else {
    section.append(element(title.includes('Fluxo') ? 'pre' : 'p', '', content || 'Não informado'));
  }
  return section;
}

function structuredOutput(record) {
  const wrap = element('div');
  const out = record.output;
  if (record.content_type === 'diagnosis') {
    wrap.append(outputSection('Hipóteses', out.hypotheses), outputSection('Evidências', out.evidence),
      outputSection('Informações faltantes', out.missing_information), outputSection('Conclusão provável', out.probable_conclusion));
  } else if (record.content_type === 'resolution') {
    wrap.append(outputSection('Procedimento', out.steps), outputSection('Quando escalar', out.escalation));
  } else if (record.content_type === 'questions') {
    wrap.append(outputSection('Perguntas priorizadas', out.questions));
  } else if (record.content_type === 'flowchart') {
    wrap.append(outputSection('Fluxo de decisão', out.ascii_flow), outputSection('Próxima ação', out.next_action));
  }
  return wrap;
}

function renderResults(records, cacheFlags = []) {
  const grid = byId('resultsGrid');
  grid.replaceChildren();
  if (!records.length) return clearWithEmpty(grid, 'Nenhuma resposta carregada.', 'Gere uma resposta para começar.');
  records.forEach((record, index) => {
    const card = element('article', 'result-card');
    const head = element('div', 'result-head');
    head.append(element('strong', '', `${typeLabels[record.content_type]} · #${record.id}`),
      element('span', `version-pill ${record.prompt_version === 'v1' ? 'muted-pill' : ''}`, record.prompt_version.toUpperCase()));
    const details = element('div', 'result-details');
    details.append(element('span', '', record.model), element('span', '', formattedDate(record.timestamp)));
    const body = element('div', 'result-body');
    const view = structuredOutput(record);
    const raw = element('pre', 'raw-json', JSON.stringify(record.output, null, 2));
    raw.hidden = true;
    body.append(view, raw);
    const actions = element('div', 'result-actions');
    const toggle = button('Ver JSON', 'button-secondary button-small', () => {
      raw.hidden = !raw.hidden;
      view.hidden = !view.hidden;
      toggle.textContent = raw.hidden ? 'Ver JSON' : 'Ver formatado';
    });
    actions.append(toggle, button('Exportar ↓', 'button-secondary button-small', () => download(
      `/runs/${record.id}/export`, `generation_${record.id}.json`
    )));
    if (cacheFlags[index]) actions.append(element('span', 'cache-hint', 'CACHE'));
    card.append(head, details, body, actions);
    grid.append(card);
  });
}

function renderReview(records) {
  state.selectedRuns = records;
  const grid = byId('reviewGrid');
  grid.replaceChildren();
  byId('comparisonSummary').hidden = true;
  byId('saveComparison').disabled = records.length !== 2 || records.some((run) => !run.evaluation);
  byId('reviewNote').textContent = records.length === 2
    ? 'Preencha e salve as duas rubricas antes da comparação.'
    : 'Para comparar, gere as duas versões do mesmo cenário.';
  if (!records.length) return clearWithEmpty(grid, 'Aguardando respostas para avaliação.', 'Abra uma execução ou gere uma comparação.');

  for (const record of records) {
    const card = element('article', 'review-card');
    const heading = element('div', 'review-header');
    heading.append(element('h3', '', `Execução #${record.id}`), element('small', '', `${record.prompt_version.toUpperCase()} / ${typeLabels[record.content_type]}`));
    const form = element('form');
    for (const [key, label, help] of rubricCriteria) {
      const field = element('label', 'rubric-item');
      const top = element('div', 'rubric-top');
      const select = element('select');
      select.name = `${key}_score`;
      select.setAttribute('aria-label', `Nota de ${label} para ${record.prompt_version}`);
      for (let grade = 1; grade <= 5; grade++) fieldOption(select, String(grade), String(grade));
      select.value = String(record.evaluation?.[key]?.score ?? 3);
      top.append(element('span', '', label), select);
      const textarea = element('textarea');
      textarea.name = `${key}_justification`;
      textarea.required = true;
      textarea.minLength = 20;
      textarea.maxLength = 400;
      textarea.rows = 3;
      textarea.placeholder = 'Cite um exemplo concreto da resposta…';
      textarea.value = record.evaluation?.[key]?.justification ?? '';
      field.append(top, element('span', 'rubric-help', help), textarea);
      form.append(field);
    }
    const submit = element('button', 'button button-secondary', record.evaluation ? 'Atualizar avaliação ↗' : 'Salvar avaliação ↗');
    submit.type = 'submit';
    form.append(submit);
    if (record.evaluation) form.append(element('div', 'saved-label', '✓ Avaliação registrada · atualize se necessário'));
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const values = new FormData(form);
      const rubric = {};
      for (const [key] of rubricCriteria) rubric[key] = {
        score: Number(values.get(`${key}_score`)), justification: String(values.get(`${key}_justification`)).trim()
      };
      submit.disabled = true;
      try {
        const updated = await request(`/runs/${record.id}/evaluation`, {method: 'PUT', body: JSON.stringify(rubric)});
        const selected = state.selectedRuns.map((run) => run.id === updated.id ? updated : run);
        renderReview(selected);
        await refreshHistory();
        message('Avaliação salva. Verifique as justificativas antes de exportar.');
      } catch (error) { message(error.message, true); submit.disabled = false; }
    });
    card.append(heading, form);
    grid.append(card);
  }
}

function renderComparison(comparison) {
  const panel = byId('comparisonSummary');
  panel.hidden = false;
  panel.className = 'summary';
  panel.replaceChildren(element('h3', '', `Comparação #${comparison.id} · ${comparison.summary.higher_scored_version.toUpperCase()}`));
  const grid = element('div', 'summary-grid');
  const summary = comparison.summary;
  for (const [title, value] of [
    ['MÉDIA V1', summary.v1_average], ['MÉDIA V2', summary.v2_average], ['DELTA V2−V1', summary.delta_v2_minus_v1]
  ]) {
    const metric = element('div', 'summary-metric');
    metric.append(element('small', '', title), element('strong', '', Number(value).toFixed(2).replace('.', ',')));
    grid.append(metric);
  }
  panel.append(grid, element('p', '', summary.disclaimer), button('Exportar comparação ↓', 'button-secondary button-small', () => download(
    `/comparisons/${comparison.id}/export`, `comparison_${comparison.id}.json`
  )));
}

async function generate(experiment) {
  if (state.busy) return;
  const payload = currentPayload();
  if (!payload.customer_id || !payload.ticket) { message('Selecione um perfil e informe o problema.', true); return; }
  setBusy(true);
  try {
    const data = await request(experiment ? '/experiments' : '/runs', {
      method: 'POST', body: JSON.stringify(payload)
    });
    const runs = experiment ? data.runs.map((item) => item.record) : [data.record];
    const cacheFlags = experiment ? data.runs.map((item) => item.cached) : [data.cached];
    renderResults(runs, cacheFlags);
    renderReview(runs);
    await refreshHistory();
    message(experiment
      ? 'As duas versões foram executadas. Leia e avalie cada resposta antes de comparar.'
      : data.cached ? 'Execução recuperada do cache.' : 'Resposta gerada e salva no histórico.');
    byId('results').scrollIntoView({behavior: 'smooth'});
  } catch (error) {
    message(error.message, true);
  } finally {
    setBusy(false);
  }
}

function openRuns(records) {
  renderResults(records);
  renderReview(records);
  byId('results').scrollIntoView({behavior: 'smooth'});
}

function renderHistory() {
  const search = byId('historySearch').value.trim().toLowerCase();
  const filter = byId('historyFilter').value;
  const runs = state.runs.filter((run) => {
    if (filter === 'evaluated' && !run.evaluation) return false;
    if (filter === 'pending' && run.evaluation) return false;
    return `${run.id} ${run.customer_id} ${run.profile?.name} ${run.prompt_version} ${run.content_type} ${run.ticket}`.toLowerCase().includes(search);
  });
  const comparisons = state.comparisons.filter((item) =>
    `${item.id} ${item.generation_ids.join(' ')} ${item.scenario_key}`.toLowerCase().includes(search)
  );
  byId('runsCount').textContent = String(runs.length);
  byId('comparisonsCount').textContent = String(comparisons.length);
  const runList = byId('historyRuns');
  const comparisonList = byId('historyComparisons');
  runList.replaceChildren();
  comparisonList.replaceChildren();
  for (const run of runs) {
    const row = element('article', 'history-item');
    const detail = element('div');
    detail.append(element('strong', '', `#${run.id} · ${run.profile?.name ?? run.customer_id} · ${typeLabels[run.content_type]}`),
      element('small', '', `${run.prompt_version} · ${run.evaluation ? 'Avaliado' : 'Pendente'} · ${formattedDate(run.timestamp)}`));
    const actions = element('div', 'history-actions');
    actions.append(button('Abrir ↗', 'button-text button-small', () => {
      const partner = state.runs.find((item) => item.scenario_key === run.scenario_key && item.prompt_version !== run.prompt_version);
      openRuns(partner ? [run, partner].sort((a, b) => a.prompt_version.localeCompare(b.prompt_version)) : [run]);
    }));
    row.append(detail, actions);
    runList.append(row);
  }
  for (const comparison of comparisons) {
    const row = element('article', 'history-item');
    const detail = element('div');
    detail.append(element('strong', '', `Comparação #${comparison.id}`),
      element('small', '', `v1 × v2 · ${formattedDate(comparison.timestamp)}`));
    row.append(detail, button('Abrir ↗', 'button-text button-small', async () => {
      try {
        const full = await request(`/comparisons/${comparison.id}`);
        openRuns(full.results);
        renderComparison(full);
      } catch (error) {message(error.message, true);}
    }));
    comparisonList.append(row);
  }
  if (!runs.length) runList.append(element('p', 'empty-caption', 'Nenhuma execução encontrada.'));
  if (!comparisons.length) comparisonList.append(element('p', 'empty-caption', 'Nenhuma comparação encontrada.'));
}

async function refreshHistory() {
  const [runs, comparisons] = await Promise.all([request('/runs'), request('/comparisons')]);
  state.runs = runs;
  state.comparisons = comparisons;
  byId('statRuns').textContent = String(runs.length);
  byId('statComparisons').textContent = String(comparisons.length);
  renderHistory();
}

async function initialize() {
  try {
    const [metadata, profiles, tickets] = await Promise.all([
      request('/meta'), request('/profiles'), request('/tickets')
    ]);
    state.profiles = profiles;
    state.tickets = tickets;
    state.isDemo = metadata.is_demo;
    byId('providerBadge').textContent = metadata.model;
    byId('providerNote').textContent = metadata.is_demo
      ? 'Respostas simuladas · não servem como teste de LLM.'
      : `API real · ${metadata.provider}. Cada nova execução pode consumir sua cota.`;
    byId('apiStatus').textContent = 'Backend online';
    byId('statMode').textContent = metadata.is_demo ? 'DEMO' : 'API REAL';
    byId('statModeHelp').textContent = metadata.model;
    byId('customer').replaceChildren();
    byId('ticketSelect').replaceChildren();
    profiles.forEach((profile) => fieldOption(byId('customer'), profile.id, `${profile.name} · ${profile.technical_level}`));
    tickets.forEach((ticket) => fieldOption(byId('ticketSelect'), ticket.id, ticket.title));
    showProfile();
    showTicket();
    await refreshHistory();
  } catch (error) {
    byId('apiStatus').textContent = 'Conexão indisponível';
    message(`${error.message} Confira a API ou configure o token de acesso.`, true);
  }
}

byId('generator').addEventListener('submit', (event) => {event.preventDefault(); generate(false);});
byId('experimentButton').addEventListener('click', () => generate(true));
byId('customer').addEventListener('change', showProfile);
byId('ticketSelect').addEventListener('change', showTicket);
byId('retryAccess').addEventListener('click', () => {
  state.token = byId('accessToken').value.trim();
  initialize();
});
byId('refreshHistory').addEventListener('click', () => refreshHistory().catch((error) => message(error.message, true)));
byId('historySearch').addEventListener('input', renderHistory);
byId('historyFilter').addEventListener('change', renderHistory);
byId('saveComparison').addEventListener('click', async () => {
  if (state.selectedRuns.length !== 2 || state.selectedRuns.some((run) => !run.evaluation)) return;
  try {
    const result = await request('/comparisons', {
      method: 'POST', body: JSON.stringify({generation_ids: state.selectedRuns.map((run) => run.id)})
    });
    renderComparison(result);
    await refreshHistory();
    message(`Comparação #${result.id} registrada. Revise as justificativas antes da entrega.`);
  } catch (error) {message(error.message, true);}
});

const observer = new IntersectionObserver((entries) => {
  for (const entry of entries) if (entry.isIntersecting) {
    document.querySelectorAll('.nav-link').forEach((link) => {
      link.classList.toggle('active', link.hash === `#${entry.target.id}`);
    });
  }
}, {rootMargin: '-20% 0px -68% 0px'});
for (const section of document.querySelectorAll('section[id]')) observer.observe(section);
initialize();
