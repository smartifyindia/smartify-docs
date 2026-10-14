export class DocumentationError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}
const fail = (status, message) => { throw new DocumentationError(status, message); };
const text = (value, max = 200) => {
  if (typeof value !== 'string' || !value.trim() || value.length > max) fail(400, 'A nonblank bounded string is required.');
  return value.trim();
};
const key = value => String(value).trim().toLowerCase().replace(/[_ -]+/g, '_');
const ecosystemAliases = { homekit: 'apple_home', apple_homekit: 'apple_home', apple_home: 'apple_home', matter: 'matter', home_assistant: 'home_assistant', alexa: 'alexa', amazon_alexa: 'alexa', google_home: 'google_home' };
const ecosystem = value => ecosystemAliases[key(value)] || key(value);
const citation = (doc, section, quote) => ({ documentId: doc.id, title: doc.title, heading: section.heading, url: doc.url + (section.anchor ? '#' + section.anchor : ''), documentHash: doc.hash, sectionHash: section.hash, quote, provenance: 'public_smartify_documentation' });
export function createDocumentationService(documents, rules) {
  function resolve(sku) {
    const found = documents.filter(doc => doc.id === sku || doc.skus.includes(sku));
    return found.length === 1 ? found[0] : null;
  }
  function evidence(doc, rule) {
    if (rule.documentHash && rule.documentHash !== doc.hash) return null;
    if (!Array.isArray(rule.evidence) || !rule.evidence.length) return null;
    const citations = [];
    for (const reference of rule.evidence) {
      const section = doc.sections.find(row => row.heading === reference.heading && row.text.includes(reference.quote));
      if (!section || !reference.quote || reference.quote.length > 800) return null;
      citations.push(citation(doc, section, reference.quote));
    }
    return citations;
  }
  return {
    document(id) {
      const doc = documents.find(row => row.id === text(id));
      if (!doc) fail(404, 'Public document not found.');
      return { ...doc, evidenceOnly: true };
    },
    search(raw) {
      const q = text(raw?.q, 200); const limit = raw.limit === undefined ? 10 : Number(raw.limit);
      if (!Number.isSafeInteger(limit) || limit < 1 || limit > 20) fail(400, 'limit must be 1–20.');
      const scoped = raw.sku === undefined ? documents : documents.filter(doc => doc.id === text(raw.sku) || doc.skus.includes(raw.sku));
      const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
      const results = scoped.flatMap(doc => doc.sections.map(section => ({ doc, section, score: terms.filter(term => (doc.title + ' ' + section.text).toLowerCase().includes(term)).length })).filter(row => row.score > 0));
      results.sort((a, b) => b.score - a.score || a.doc.id.localeCompare(b.doc.id) || a.section.heading.localeCompare(b.section.heading));
      return { query: q, items: results.slice(0, limit).map(({ doc, section }) => ({ ...citation(doc, section, section.text.slice(0, 1200)), skus: doc.skus })), hasMore: results.length > limit, evidenceOnly: true };
    },
    compatibility(raw) {
      if (!Array.isArray(raw?.skus) || raw.skus.length < 1 || raw.skus.length > 10) fail(400, 'Provide 1–10 exact SKUs or document IDs.');
      const skus = raw.skus.map(sku => text(sku));
      if (new Set(skus).size !== skus.length) fail(400, 'Duplicate SKU.');
      const platform = raw.ecosystem === undefined ? null : ecosystem(text(raw.ecosystem, 100));
      const useCase = raw.useCase === undefined ? null : key(text(raw.useCase, 200));
      if (!platform && !useCase) fail(400, 'Provide ecosystem or useCase.');
      const items = skus.map(sku => {
        const doc = resolve(sku);
        const unknown = reason => ({ sku, status: 'unknown', mode: null, conditions: [], reason, citations: doc ? doc.sections.filter(row => /specification|description|requirement|load/i.test(row.heading)).slice(0, 3).map(section => citation(doc, section, section.text.slice(0, 800))) : [] });
        if (!doc) return unknown('Exact product documentation is missing or ambiguous.');
        // Match only explicitly reviewed facts; prose and protocol labels cannot create rules.
        const facts = rules.filter(rule => rule.documentId === doc.id && ((platform && rule.ecosystem === platform && !rule.useCase) || (useCase && rule.useCase === useCase && !rule.ecosystem)));
        const checked = facts.map(rule => ({ rule, citations: evidence(doc, rule) })).filter(row => row.citations);
        if ((platform && !checked.some(row => row.rule.ecosystem === platform)) || (useCase && !checked.some(row => row.rule.useCase === useCase))) return unknown('No current reviewed rule covers all requested compatibility dimensions.');
        const contradictory = checked.some(({ rule }) => checked.some(({ rule: other }) => rule.ecosystem === other.ecosystem && rule.useCase === other.useCase && (rule.status !== other.status || rule.mode !== other.mode)));
        if (checked.some(row => row.rule.status === 'unknown') || contradictory) {
          return { ...unknown('Documentation conflicts; resolve the cited evidence before confirming compatibility.'), citations: checked.flatMap(row => row.citations) };
        }
        const status = checked.some(row => row.rule.status === 'unsupported') ? 'unsupported' : checked.some(row => row.rule.status === 'conditional') ? 'conditional' : 'supported';
        return { sku, status, mode: checked.find(row => row.rule.mode)?.rule.mode || null, conditions: [...new Set(checked.flatMap(row => row.rule.conditions || []))], reason: status === 'conditional' ? 'Documented prerequisites require verification for this installation.' : 'Explicitly documented for the requested scope.', citations: checked.flatMap(row => row.citations) };
      });
      // Multi-product reports evaluate each product only, never certify interoperability between them.
      const status = items.some(item => item.status === 'unknown') ? 'unknown' : items.some(item => item.status === 'unsupported') ? 'unsupported' : items.some(item => item.status === 'conditional') ? 'conditional' : 'supported';
      return { status, ecosystem: platform, useCase, items, pairwiseCompatibility: 'not_assessed', evidenceOnly: true };
    },
  };
}
