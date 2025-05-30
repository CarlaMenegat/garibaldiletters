const annotationFiles = {
  comment: 'annotations/annotations_comments.xml',
  place: 'annotations/annotations_places.xml',
  person: 'annotations/annotations_persons.xml',
  org: 'annotations/annotations_org.xml',
  date: 'annotations/annotations_dates.xml',
  physical: 'annotations/annotations_physical.xml',
  publisher: 'annotations/annotations_publishers.xml' 
};
  
  const basePath = 'letters/';
  const annotationData = {};
  const TEI_NS = 'http://www.tei-c.org/ns/1.0';
  
  async function loadXML(path) {
    const response = await fetch(path);
    if (!response.ok) throw new Error(`Failed to fetch ${path}`);
    const text = await response.text();
    return new window.DOMParser().parseFromString(text, 'application/xml');

    const keywords = header?.getElementsByTagNameNS(TEI_NS, 'term');
    let themes = [];

      if (keywords) {
        for (let term of keywords) {
          const ana = term.getAttribute('ana')?.replace(/^#/, '');
          const doc = annotationData['theme'];
          const categories = doc?.getElementsByTagNameNS(TEI_NS, 'category') || [];

          for (let cat of categories) {
            if (cat.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id') === ana) {
              const desc = cat.getElementsByTagNameNS(TEI_NS, 'catDesc')[0]?.textContent;
              if (desc) themes.push(desc);
            }
          }
        }
      }

  const themeEntry = `
    <div class="mb-3">
      <strong>General Theme:</strong><br>
      ${themes.length ? themes.join(', ') : '(not specified)'}
    </div>`;
  }
  function activateAnnotationClicks(container) {
    container.querySelectorAll('.annotated').forEach(el => {
      el.addEventListener('click', () => {
        const desc = el.dataset.desc;
        const type = el.dataset.type;
        document.getElementById('annotations-content').innerHTML = `
          <div class="annotation-box ${type}">
            <strong>${type.toUpperCase()}</strong><br>${desc}
          </div>`;
        document.getElementById('annotations-box')?.classList.remove('d-none');
        document.querySelector('.transcription-box')?.classList.add('with-annotations');
      });
    });
  }

  async function loadAnnotationFile(type, path) {
    try {
      const doc = await loadXML(path);
      annotationData[type] = doc;
      console.log(`[✓] Loaded annotation for '${type}' from '${path}'`);
    } catch (err) {
      console.warn(`[!] Failed to load annotation for '${type}' from '${path}':`, err);
    }
  }
  
  async function preloadAnnotationData() {
    const loadPromises = Object.entries(annotationFiles).map(
      ([type, path]) => loadAnnotationFile(type, path)
    );
    await Promise.all(loadPromises);
  }
  
  function extractDescriptionFromRef(type, ref) {
    const id = ref.replace(/^#/, '');
    const doc = annotationData[type];
    if (!doc) return ref;
  
    if (type === 'person') {
      const persons = doc.getElementsByTagNameNS(TEI_NS, 'person');
      for (let person of persons) {
        const xmlId = person.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id');
        if (xmlId === id) {
          const full = person.querySelector("persName[type='full']")?.textContent || 'No full name';
          const epithet = person.querySelector("persName[type='epithet']")?.textContent || 'No epithet';
          const idnos = person.getElementsByTagNameNS(TEI_NS, 'idno');
          let viaf = '';
          for (let idno of idnos) {
            if (idno.getAttribute('type') === 'VIAF') {
              viaf = idno.textContent;
            }
          }
          let desc = `${full} – ${epithet}`;
          if (viaf) {
            desc += `<br><a href="${viaf}" target="_blank">VIAF profile</a>`;
          }
          return desc;
        }
      }
    }
  
    if (type === 'org') {
      const orgs = doc.getElementsByTagNameNS(TEI_NS, 'org');
      for (let org of orgs) {
        const xmlId = org.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id');
        if (xmlId === id) {
          const orgName = org.querySelector('orgName')?.textContent || 'No organization name';
          const note = org.querySelector('note')?.textContent || '';
          const idnos = org.getElementsByTagNameNS(TEI_NS, 'idno');
          let link = '';
          for (let idno of idnos) {
            if (idno.getAttribute('type') === 'VIAF') {
              link = idno.textContent;
            }
          }
          let desc = orgName;
          if (note) {
            desc += `<br><em>${note}</em>`;
          }
          if (link) {
            desc += `<br><a href="${link}" target="_blank">VIAF profile</a>`;
          }
          return desc;
        }
      }
    }
  
    if (type === 'place') {
      const places = doc.getElementsByTagNameNS(TEI_NS, 'place');
      for (let place of places) {
        if (place.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id') === id) {
          const name = place.getElementsByTagNameNS(TEI_NS, 'placeName')[0]?.textContent || '';
          const geo = place.getElementsByTagNameNS(TEI_NS, 'geo')[0]?.textContent || '';
          const note = place.getElementsByTagNameNS(TEI_NS, 'note')[0]?.textContent || '';
          const idnos = place.getElementsByTagNameNS(TEI_NS, 'idno');
          let geoname = '';
          for (let idno of idnos) {
            if (idno.getAttribute('type') === 'geonames') {
              geoname = idno.textContent;
            }
          }
          let desc = name;
          if (note) desc += `<br>${note}`;
          if (geoname) desc += `<br><a href="${geoname}" target="_blank">See on GeoNames</a>`;
          if (geo) desc += `<br>Coordinates: ${geo}`;
          return desc;
        }
      }
    }
  
    if (type === 'date') {
      const dates = doc.getElementsByTagNameNS(TEI_NS, 'date');
      for (let date of dates) {
        const xmlId = date.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id');
        if (xmlId === id) {
          const when = date.getAttribute('when') || '';
          const desc = date.querySelector('desc')?.textContent || '(no description)';
          return `${when}<br>${desc}`;
        }
      }
    }
  
    return ref;
  }
  
  function renderTEIText(node) {
    let html = '';
    node.childNodes.forEach(child => {
      if (child.nodeType === 1) {
        const tag = child.tagName.split(':').pop();
        const ref = child.getAttribute('ref');
        const tagContent = renderTEIText(child);
        const classMap = {
          'persName': 'person',
          'placeName': 'place',
          'orgName': 'org',
          'date': 'date'
        };
  
        if (ref && tag in classMap) {
          const desc = extractDescriptionFromRef(classMap[tag], ref);
          html += `<span class="annotated ${classMap[tag]}" data-type="${classMap[tag]}" data-desc="${desc.replace(/"/g, '&quot;')}">${tagContent}</span>`;
          return;
        }
  
        switch (tag) {
          case 'p': {
            const xmlId = child.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id');
            const content = renderTEIText(child);
            html += `<p id="${xmlId || ''}">${content || '[see physical note]'}</p>`;
            break;
          }
          case 'lb': html += '<br/>'; break;
          case 'date': {
            const xmlId = child.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id');
            const content = renderTEIText(child);
            html += `<span id="${xmlId || ''}">${content}</span>`;
            break;
          }
          case 'seg': {
            const ana = child.getAttribute('ana');
            const xmlId = child.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id');
            const content = renderTEIText(child);
  
            if (ana && xmlId) {
              const id = ana.replace(/^#/, '');
              const doc = annotationData['comment'];  // 👈 USA O ARQUIVO DE COMENTÁRIOS
              let desc = '(no description)';
  
              if (doc) {
                const categories = doc.getElementsByTagNameNS(TEI_NS, 'category');
                for (let category of categories) {
                  const catId = category.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id');
                  if (catId === id) {
                    desc = category.getElementsByTagNameNS(TEI_NS, 'catDesc')[0]?.textContent || '(no description)';
                    break;
                  }
                }
              }
  
              html += `<span id="${xmlId}" class="annotated comment" data-type="comment" data-desc="${desc.replace(/"/g, '&quot;')}">${content}</span>`;
            } else {
              html += content;
            }
            break;
          }
          case 'choice': {
            const corr = child.querySelector('corr');
            const expan = child.querySelector('expan');
            if (corr) html += renderTEIText(corr);
            else if (expan) html += renderTEIText(expan);
            else html += renderTEIText(child);
            break;
          }
          default:
            html += renderTEIText(child);
        }
      } else if (child.nodeType === 3) {
        html += child.textContent;
      }
    });
    return html;
  }
  async function applyAnnotations(container, fileName) {
    const allSpans = [];
  
    for (const [type, doc] of Object.entries(annotationData)) {
      const spans = doc.querySelectorAll('spanGrp > span');
      spans.forEach(span => {
        const from = span.getAttribute('from');
        if (!from.includes(fileName)) return;
  
        const match = from.match(/#(.*)$/);
        if (!match) return;
        const id = match[1];
        let desc = '(no description)';
  
        if (type === 'date') {
          const ana = span.getAttribute('ana')?.replace(/^#/, '');
          const events = doc.getElementsByTagNameNS(TEI_NS, 'event');
          for (let event of events) {
            const xmlId = event.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id');
            if (xmlId === ana) {
              desc = event.getElementsByTagNameNS(TEI_NS, 'desc')[0]?.textContent || '(no description)';
              break;
            }
          }
        }
  
        if (type === 'physical') {
          desc = span.getElementsByTagNameNS(TEI_NS, 'desc')[0]?.textContent || '(no description)';
        }
  
        if (type === 'comment') {
          const ana = span.getAttribute('ana')?.replace(/^#/, '');
          const categories = doc.getElementsByTagNameNS(TEI_NS, 'category');
          for (let cat of categories) {
            const catId = cat.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id');
            if (catId === ana) {
              desc = cat.getElementsByTagNameNS(TEI_NS, 'catDesc')[0]?.textContent || '(no description)';
              break;
            }
          }
        }
  
        allSpans.push({ id, type, desc });
      });
    }
  
    allSpans.forEach(({ id, type, desc }) => {
      const target = container.querySelector(`#${id}`);
      if (target && !target.classList.contains('annotated')) {
        const original = target.innerHTML;
        target.innerHTML = `<span class="annotated ${type}" data-type="${type}" data-desc="${desc.replace(/"/g, '&quot;')}">${original}</span>`;
      }
    });
  
    container.querySelectorAll('.annotated').forEach(el => {
      el.addEventListener('click', () => {
        const desc = el.dataset.desc;
        const type = el.dataset.type;
        document.getElementById('annotations-content').innerHTML = `
          <div class="annotation-box ${type}">
            <strong>${type.toUpperCase()}</strong><br>${desc}
          </div>`;
        document.getElementById('annotations-box')?.classList.remove('d-none');
        document.querySelector('.transcription-box')?.classList.add('with-annotations');
      });
    });
  }

  function updateTextForSurface(surfaceId, fileName) {
    const container = document.getElementById('transcription-content');
    const teiDoc = annotationData['_teiDoc']; // armazenamos na renderViewer
    const divs = teiDoc.getElementsByTagNameNS(TEI_NS, 'div');
  
    let matchedDiv = null;
    for (let div of divs) {
      const corresp = div.getAttribute('corresp');
      if (corresp === `#${surfaceId}`) {
        matchedDiv = div;
        break;
      }
    }
  
    if (matchedDiv) {
      const html = renderTEIText(matchedDiv);
      container.innerHTML = html;
      applyAnnotations(container, fileName);
  
      // Verifica anotações físicas associadas
      const physicalAnnotations = [];
      const doc = annotationData['physical'];
      if (doc) {
        const spans = doc.querySelectorAll('spanGrp[type="physical"] > span');
        spans.forEach(span => {
          const from = span.getAttribute('from');
          if (from === `${fileName}#${surfaceId}`) {
            const desc = span.getElementsByTagNameNS(TEI_NS, 'desc')[0]?.textContent || '(no description)';
            physicalAnnotations.push(desc);
          }
        });
      }
  
      if (physicalAnnotations.length > 0) {
        const annotationBox = document.getElementById('annotations-content');
        annotationBox.innerHTML += `
          <div class="annotation-box physical">
            <strong>PHYSICAL</strong><br>
            ${physicalAnnotations.join('<br><hr>')}
          </div>`;
        document.getElementById('annotations-box')?.classList.remove('d-none');
        document.querySelector('.transcription-box')?.classList.add('with-annotations');
      }
  
      const plainText = matchedDiv.textContent.trim();
      if (plainText === '[see physical note]') {
        const annotationBox = document.getElementById('annotations-content');
        annotationBox.innerHTML = `
          <div class="annotation-box physical">
            <strong>PHYSICAL</strong><br>Blank page.
          </div>`;
        document.getElementById('annotations-box')?.classList.remove('d-none');
        document.querySelector('.transcription-box')?.classList.add('with-annotations');
      } else {
        document.getElementById('annotations-box')?.classList.add('d-none');
        document.querySelector('.transcription-box')?.classList.remove('with-annotations');
      }
  
      // 🆕 Integração com abas de transcrição/tradução
      originalHTML = html;
      translationHTMLs = {};
      setupTranscriptionTabs(fileName, surfaceId);

      if (currentTab === 'translation') {
        document.getElementById('tab-translation')?.click();
      } else {
        const container = document.getElementById('transcription-content');
        container.innerHTML = originalHTML;
        applyAnnotations(container, fileName);
      }
    }
  }

  let originalHTML = '';
  let translationHTMLs = {};
  let currentTab = 'original';

// Função para carregar e renderizar a tradução
async function loadTranslationXML(fileName, surfaceId) {
  try {
    const base = fileName.endsWith('.xml') ? fileName.slice(0, -4) : fileName;
    const translatedFile = `${base}_en.xml`;
    const translationDoc = await loadXML(`letters/${translatedFile}`);
    const divs = translationDoc.getElementsByTagNameNS(TEI_NS, 'div');
    const matchedDiv = Array.from(divs).find(div => div.getAttribute('corresp') === `#${surfaceId}`);

    if (matchedDiv) {
      return renderTEIText(matchedDiv);
    } else {
      return '<p><em>(Translation not available for this page)</em></p>';
    }
  } catch (err) {
    console.warn(`Translation file not found: ${fileName}`, err);
    return '<p><em>(Translation not available)</em></p>';
  }
}

// Função para configurar as abas após carregar uma superfície
function setupTranscriptionTabs(fileName, surfaceId) {
  const tabOriginal = document.getElementById('tab-original');
  const tabTranslation = document.getElementById('tab-translation');
  const container = document.getElementById('transcription-content');

  // Remove eventos antigos para evitar múltiplos listeners
  tabOriginal.replaceWith(tabOriginal.cloneNode(true));
  tabTranslation.replaceWith(tabTranslation.cloneNode(true));

  const newTabOriginal = document.getElementById('tab-original');
  const newTabTranslation = document.getElementById('tab-translation');

  // Aba ORIGINAL
  newTabOriginal.addEventListener('click', () => {
    container.innerHTML = originalHTML;
    currentTab = 'original';
    updateTabStyle();
  });

  // Aba TRANSLATION
  newTabTranslation.addEventListener('click', async () => {
    if (!translationHTMLs[surfaceId]) {
      const rawHTML = await loadTranslationXML(fileName, surfaceId);

      // Cria container temporário e aplica anotações
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = rawHTML;
      applyAnnotations(tempDiv, fileName);
      activateAnnotationClicks(tempDiv);
      translationHTMLs[surfaceId] = tempDiv.innerHTML;

      translationHTMLs[surfaceId] = tempDiv.innerHTML;
    }

    container.innerHTML = `<div class="translated-text">${translationHTMLs[surfaceId]}</div>`;
    activateAnnotationClicks(container);
    currentTab = 'translation';
    updateTabStyle();
  });

  updateTabStyle();
}

// Função auxiliar para estilizar abas ativas
function updateTabStyle() {
  document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
  document.getElementById(`tab-${currentTab}`)?.classList.add('active');
}

  // === IIIF viewer ===
  let iiifImages = [];
  let currentIndex = 0;
  
  async function loadIIIFManifest(manifestUrl) {
    try {
      console.log("Loading IIIF manifest:", manifestUrl);
  
      Mirador.viewer({
        id: 'iiif-viewer',
        windows: [{
          manifestId: manifestUrl,
          canvasIndex: 0,
          allowClose: false,
          allowMaximize: false,
          allowFullscreen: true,
          thumbnailNavigationPosition: 'far-bottom'
        }],
        workspaceControlPanel: {
          enabled: false
        },
        window: {
          defaultSideBarPanel: 'info',
          sideBarOpenByDefault: false
        }
      });
  
      // Listen to canvas changes and sync transcription
      window.setTimeout(() => {
        const miradorStore = window.Mirador.store;
        if (miradorStore) {
          miradorStore.subscribe(() => {
            const state = miradorStore.getState();
            const windows = Object.values(state.windows || {});
            const canvasIndex = windows[0]?.canvasIndex;
            const manifest = windows[0]?.manifestId;
  
            // Convert canvas index to surface ID
            const surfaceId = `surface-${canvasIndex + 1}`;
            updateTextForSurface(surfaceId, window.currentLetterFileName);
          });
        }
      }, 1000);
  
    } catch (err) {
      console.error("Failed to load Mirador viewer:", err);
    }
  }
  
    function displayIIIFImage() {
        if (iiifImages.length > 0) {
        const imgElement = document.getElementById('iiif-image');
        if (imgElement) {
            imgElement.src = iiifImages[currentIndex];
            console.log("Exibindo imagem:", iiifImages[currentIndex]);
        }
        }
    }
  
  
    async function renderViewer(fileName) {
      const teiDoc = await loadXML(basePath + fileName);
      annotationData['_teiDoc'] = teiDoc; // armazena o documento TEI completo
      window.currentLetterFileName = fileName;
    
      // 🆕 Zera variáveis globais de conteúdo
      originalHTML = '';
      translationHTMLs = {};
      currentTab = 'original';
    
      document.getElementById('transcription-content').innerHTML = '';
      document.getElementById('annotations-content').innerHTML = '';
    
      const divs = teiDoc.getElementsByTagNameNS(TEI_NS, 'div');
      const selector = document.getElementById('surface-selector');
      selector.innerHTML = '';
    
      let firstSurfaceId = null;
    
      // Preenche o seletor de superfícies
      Array.from(divs).forEach(div => {
        const corresp = div.getAttribute('corresp');
        if (corresp?.startsWith('#surface-')) {
          const surfaceId = corresp.slice(1);
          const option = document.createElement('option');
          option.value = surfaceId;
          option.textContent = surfaceId.replace('surface-', 'Page ');
          selector.appendChild(option);
    
          if (!firstSurfaceId) {
            firstSurfaceId = surfaceId;
          }
        }
      });
    
      // Atualiza conteúdo da primeira superfície
      if (firstSurfaceId) {
        selector.value = firstSurfaceId;
        updateTextForSurface(firstSurfaceId, fileName);
      }
    
      // === IIIF Viewer ===
      const sourceDesc = teiDoc.getElementsByTagNameNS(TEI_NS, 'sourceDesc')[0];
      const ptr = sourceDesc?.getElementsByTagNameNS(TEI_NS, 'ptr')[0];
      const manifestUrl = ptr?.getAttribute('target');
    
      if (manifestUrl) {
        loadIIIFManifest(manifestUrl);
      }
    
      // === Metadata lateral
      fillMetadataPanel(fileName);
    }

  let letters = [];
  let letterIndex = 0;
  translationHTMLs = {};// limpa a tradução da carta anterior
  currentTab = 'original';

function formatDate(place, dateStr) {
  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];
  const date = new Date(dateStr);
  const day = date.getDate();
  const month = months[date.getMonth()];
  const year = date.getFullYear();
  return `${place}, ${day} ${month} ${year}`;
}

function updateLetterView(index) {
  letterIndex = index; // 👈 ATUALIZA PRIMEIRO

  const letter = letters[index];
  renderViewer(letter.file);
  document.getElementById('letter-date').textContent = formatDate(letter.place, letter.date);
  document.getElementById('prev-letter').disabled = index === 0;
  document.getElementById('next-letter').disabled = index === letters.length - 1;
}

function setupLetterNavigation() {
  const urlParams = new URLSearchParams(window.location.search);
  const fileParam = urlParams.get('file');

  fetch('letters_order.json')
    .then(res => res.json())
    .then(data => {
      letters = data;

      // Se houver um parâmetro ?file=..., procura o índice correspondente
      if (fileParam) {
        const index = letters.findIndex(l => l.file === fileParam);
        if (index !== -1) {
          updateLetterView(index); // Abre a carta especificada
          return;
        } else {
          console.warn(`Arquivo '${fileParam}' não encontrado em letters_order.json`);
        }
      }

      // Se não houver parâmetro ou não encontrar o arquivo, abre a primeira carta
      updateLetterView(0);
    });

  document.getElementById('prev-letter').addEventListener('click', () => {
    if (letterIndex > 0) updateLetterView(letterIndex - 1);
  });

  document.getElementById('next-letter').addEventListener('click', () => {
    if (letterIndex < letters.length - 1) updateLetterView(letterIndex + 1);
  });
}

// Altere seu DOMContentLoaded para isso:
document.addEventListener('DOMContentLoaded', () => {
  preloadAnnotationData().then(() => {
    setupLetterNavigation();
  });

  const closeBtn = document.getElementById('close-annotations');
  closeBtn?.addEventListener('click', () => {
    document.getElementById('annotations-box')?.classList.add('d-none');
    document.querySelector('.transcription-box')?.classList.remove('with-annotations');
  });

  document.getElementById('prev-image')?.addEventListener('click', () => {
    if (currentIndex > 0) {
      currentIndex--;
      displayIIIFImage();
    }
  });

  document.getElementById('next-image')?.addEventListener('click', () => {
    if (currentIndex < iiifImages.length - 1) {
      currentIndex++;
      displayIIIFImage();
    }
  });

  document.getElementById('surface-selector')?.addEventListener('change', function () {
    const selectedSurface = this.value;
    updateTextForSurface(selectedSurface, window.currentLetterFileName);
  });

  // 🆕 Controles da sidebar de metadados
  const toggleSidebarBtn = document.getElementById('toggle-sidebar');
  const sidebar = document.getElementById('metadata-sidebar');
  const closeSidebarBtn = document.getElementById('close-sidebar');
  const mainContent = document.querySelector('.main-content');

  toggleSidebarBtn?.addEventListener('click', () => {
    sidebar.classList.add('open');
    mainContent.classList.add('sidebar-open');
  });

  closeSidebarBtn?.addEventListener('click', () => {
    sidebar.classList.remove('open');
    mainContent.classList.remove('sidebar-open');
  });
});


function fillMetadataPanel(fileName) {
  const container = document.getElementById('metadata-content');
  container.innerHTML = '';

  loadXML(basePath + fileName).then(teiDoc => {
    const header = teiDoc.getElementsByTagNameNS(TEI_NS, 'teiHeader')[0];

    // === IIIF Manifest ===
    const ptr = teiDoc.getElementsByTagNameNS(TEI_NS, 'ptr')[0];
    const manifestUrl = ptr?.getAttribute('target') || '';
    const iiifEntry = `
      <div class="mb-3">
        <strong>IIIF Manifest:</strong><br>
        <a href="${manifestUrl}" target="_blank">
          <img src="images/IIIFlogo.png" alt="IIIF" style="height: 24px;">
        </a>
      </div>`;

    // === From (fixo) ===
    const fromEntry = `
      <div class="mb-3">
        <strong>From:</strong><br>
        <span>Giuseppe Garibaldi</span>
      </div>`;

    // === To ===
    let to = '(desconhecido)';
    const corresp = header?.getElementsByTagNameNS(TEI_NS, 'correspAction');
    for (let el of corresp) {
      if (el.getAttribute('type') === 'received') {
        const org = el.getElementsByTagNameNS(TEI_NS, 'orgName')[0]?.textContent;
        const person = el.getElementsByTagNameNS(TEI_NS, 'persName')[0]?.textContent;
        const place = el.getElementsByTagNameNS(TEI_NS, 'placeName')[0]?.textContent;
        to = org || person || place || to;
        break;
      }
    }
    const toEntry = `
      <div class="mb-3">
        <strong>To:</strong><br>
        <span>${to}</span>
      </div>`;

    // === Sent from ===
    let sentFrom = '(local não identificado)';
    let sentFromLink = '';
    const placeEl = header?.getElementsByTagNameNS(TEI_NS, 'placeName')[0];
    if (placeEl) {
      sentFrom = placeEl.textContent;
      const doc = annotationData['place'];
      const places = doc?.getElementsByTagNameNS(TEI_NS, 'place') || [];

      for (let place of places) {
        const name = place.getElementsByTagNameNS(TEI_NS, 'placeName')[0]?.textContent;
        if (name?.trim().toLowerCase() === sentFrom.trim().toLowerCase()) {
          const idnos = place.getElementsByTagNameNS(TEI_NS, 'idno');
          for (let idno of idnos) {
            if (idno.getAttribute('type') === 'geonames') {
              sentFromLink = idno.textContent;
            }
          }
          break;
        }
      }
    }
    const sentFromEntry = `
      <div class="mb-3">
        <strong>Sent from:</strong><br>
        ${sentFromLink ? `<a href="${sentFromLink}" target="_blank">${sentFrom}</a>` : sentFrom}
      </div>`;

    // === Conservation Place ===
    const publisher = header?.getElementsByTagNameNS(TEI_NS, 'publisher')[0]?.textContent || '(não informado)';
    let publisherLink = '';
    const publishersDoc = annotationData['publisher'];
    const publisherOrgs = publishersDoc?.getElementsByTagNameNS(TEI_NS, 'org') || [];

    for (let org of publisherOrgs) {
      const name = org.getElementsByTagNameNS(TEI_NS, 'orgName')[0]?.textContent;
      if (name === publisher) {
        publisherLink = org.getElementsByTagNameNS(TEI_NS, 'idno')[0]?.textContent || '';
        break;
      }
    }
    const conservationEntry = `
      <div class="mb-3">
        <strong>Conservation Place:</strong><br>
        ${publisherLink ? `<a href="${publisherLink}" target="_blank">${publisher}</a>` : publisher}
      </div>`;

    // === General Theme (termo clicável com descrição oculta) ===
    const keywords = header?.getElementsByTagNameNS(TEI_NS, 'term');
    let themeItems = [];

    if (keywords) {
      for (let i = 0; i < keywords.length; i++) {
        const term = keywords[i];
        const ana = term.getAttribute('ana')?.replace(/^#/, '');
        const termLabel = term.textContent || '(term not informed)';
        let description = '(no description)';
        const doc = annotationData['theme'];
        const categories = doc?.getElementsByTagNameNS(TEI_NS, 'category') || [];

        for (let cat of categories) {
          const catId = cat.getAttributeNS('http://www.w3.org/XML/1998/namespace', 'id');
          if (catId === ana) {
            description = cat.getElementsByTagNameNS(TEI_NS, 'catDesc')[0]?.textContent || description;
            break;
          }
        }

        const itemHtml = `
          <div class="theme-toggle metadata-entry">
            <span class="theme-term" style="cursor:pointer;text-decoration:underline dotted;" onclick="this.nextElementSibling.classList.toggle('d-none');">
              ${termLabel}
            </span>
            <div class="theme-description d-none small mt-1" style="padding-left:10px;">
              ${description}
            </div>
          </div>`;
        themeItems.push(itemHtml);
      }
    }

    const themeEntry = `
      <div class="mb-3">
        <strong>General Theme:</strong><br>
        ${themeItems.length ? themeItems.join('') : '(not specified)'}
      </div>`;

      const baseFile = fileName.replace('.xml', '');
      const rdfEntry = `
        <div class="mb-3">
          <strong>Download RDF:</strong><br>
          <a href="rdf/${baseFile}.ttl" download>📄 Turtle (.ttl)</a><br>
          <a href="rdf/${baseFile}.rdf" download>📄 RDF/XML (.rdf)</a><br>
          <a href="rdf/${baseFile}.jsonld" download>📄 JSON-LD (.jsonld)</a>
        </div>`;
      
      const xmlDownloadEntry = `
        <div class="mb-3">
          <strong>Download XML:</strong><br>
          <a href="letters/${fileName}" download>📜 Original XML</a><br>
          <a href="letters/${fileName.replace('.xml', '_en.xml')}" download>📜 Translated XML (English)</a>
        </div>`;

    // === Montagem final dos metadados ===
    container.innerHTML = `
      <div class="metadata-entry">${iiifEntry}</div>
      <div class="metadata-entry">${fromEntry}</div>
      <div class="metadata-entry">${toEntry}</div>
      <div class="metadata-entry">${sentFromEntry}</div>
      <div class="metadata-entry">${conservationEntry}</div>
      ${themeEntry}
      <div class="metadata-entry">${rdfEntry}</div>
      <div class="metadata-entry">${xmlDownloadEntry}</div>
    `;
  });
}