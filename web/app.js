const $ = id => document.getElementById(id);
const modes = ['bm25', 'semantic', 'hybrid'];
function node(tag, text, cls) { const el = document.createElement(tag); el.textContent = text; if (cls) el.className = cls; return el; }
function link(text, url) { const a = node('a', text); try { const parsed = new URL(url); if (['http:', 'https:'].includes(parsed.protocol)) { a.href = parsed.href; a.target = '_blank'; a.rel = 'noopener noreferrer'; } } catch {} return a; }
function renderResults(mode, rows) {
  const list = $(`${mode}-results`); list.replaceChildren();
  if (!rows?.length) { list.append(node('li', rows ? 'No keyword matches. Try different words.' : 'Unavailable. See the message above and try again.', 'empty')); return; }
  rows.forEach((row, i) => {
    const item = node('li', '', 'result'); const head = node('div', '', 'result-head');
    head.append(node('span', `Rank ${i + 1}`), node('span', `Passage ${row.id + 1}`));
    const title = node('h4', ''); title.append(link(row.title, row.url));
    const label = mode === 'bm25' ? 'BM25' : mode === 'semantic' ? 'Cosine similarity' : 'Fusion score';
    item.append(head, title, node('div', `${label}: ${row.score.toFixed(mode === 'hybrid' ? 5 : 3)}`, 'score'), node('p', row.text.slice(0, 240) + (row.text.length > 240 ? '…' : ''), 'excerpt'));
    const details = node('details', ''); details.append(node('summary', 'Read full passage'), node('p', row.text)); item.append(details); list.append(item);
  });
}
document.querySelectorAll('[data-question]').forEach(button => button.addEventListener('click', () => { $('question').value = button.dataset.question; $('question').focus(); }));
fetch('/api/status').then(async response => { const data = await response.json(); if (!response.ok) throw new Error(data.error); $('index-status').textContent = `${data.sources} sources · ${data.chunks} passages indexed`; }).catch(error => { $('index-status').textContent = 'Index unavailable'; $('error').textContent = error.message; $('error').hidden = false; });
$('search-form').addEventListener('submit', async event => {
  event.preventDefault(); const question = $('question').value.trim();
  if (!question) { $('question').focus(); return; }
  $('submit').disabled = true; $('submit').textContent = 'Searching…'; $('error').hidden = true; $('answer-section').hidden = true;
  $('progress').textContent = $('generate').checked ? 'Comparing all three methods and preparing your answer. This may take a minute…' : 'Comparing keyword and semantic matches…';
  $('result-status').textContent = 'Searching…'; $('result-question').hidden = true;
  modes.forEach(mode => { $(`${mode}-results`).replaceChildren(node('li', 'Searching your collection…', 'empty')); });
  const controller = new AbortController(); const timeout = setTimeout(() => controller.abort(), 420000);
  try {
    const response = await fetch('/api/compare', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question, top_k:Number($('top-k').value), generate:$('generate').checked}), signal:controller.signal});
    const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Search failed. Please try again.');
    modes.forEach(mode => renderResults(mode, data.results[mode]));
    $('result-question').textContent = data.question; $('result-question').hidden = false;
    $('result-status').textContent = 'Ranked by relevance';
    if (data.answer) { $('answer').textContent = data.answer; $('citations').replaceChildren(); data.results.hybrid.forEach((row, i) => $('citations').append(link(`[${i + 1}] Passage ${row.id + 1}`, row.url))); $('answer-section').hidden = false; }
    const errors = Object.values(data.errors); if (errors.length) { $('error').textContent = errors.join(' '); $('error').hidden = false; }
    $('progress').textContent = errors.length ? 'Comparison finished with some results unavailable.' : 'Comparison complete.';
  } catch (error) {
    $('error').textContent = error.name === 'AbortError' ? 'The request timed out. Please try again without an answer.' : error.message;
    $('error').hidden = false; $('progress').textContent = ''; $('result-status').textContent = 'Search unsuccessful'; modes.forEach(mode => renderResults(mode, undefined));
  } finally { clearTimeout(timeout); $('submit').disabled = false; $('submit').textContent = 'Ask & compare'; }
});
