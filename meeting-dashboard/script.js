// Firebase Config
const firebaseConfig = {
  apiKey: "AIzaSyAa896vxlGPhun8t64c36zcrCJYl42wh38",
  authDomain: "meeting-dashboard-comunicacion.firebaseapp.com",
  projectId: "meeting-dashboard-comunicacion",
  storageBucket: "meeting-dashboard-comunicacion.firebasestorage.app",
  messagingSenderId: "710360322334",
  appId: "1:710360322334:web:352730760e7503c9c0790f"
};

firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// Estado global
let currentMeetingId = null;
let meetings = [];
let backlogItems = [];
let unsubscribeMeetings = null;
let unsubscribeBacklog = null;

// DOM Elements
const newMeetingBtn = document.getElementById('newMeetingBtn');
const newMeetingModal = document.getElementById('newMeetingModal');
const confirmNewMeetingBtn = document.getElementById('confirmNewMeetingBtn');
const cancelNewMeetingBtn = document.getElementById('cancelNewMeetingBtn');
const newMeetingDateInput = document.getElementById('newMeetingDate');

const meetingsList = document.getElementById('meetingsList');
const backlogList = document.getElementById('backlogList');
const emptyState = document.getElementById('emptyState');
const meetingDetail = document.getElementById('meetingDetail');

const meetingDate = document.getElementById('meetingDate');
const topicsInMeeting = document.getElementById('topicsInMeeting');
const notesField = document.getElementById('notesField');
const nextStepsField = document.getElementById('nextStepsField');
const saveMeetingBtn = document.getElementById('saveMeetingBtn');
const deleteMeetingBtn = document.getElementById('deleteMeetingBtn');

const newBacklogItemInput = document.getElementById('newBacklogItemInput');
const addBacklogItemBtn = document.getElementById('addBacklogItemBtn');
const notesDropContainer = document.getElementById('notesDropContainer');

// Event Listeners
newMeetingBtn.addEventListener('click', openNewMeetingModal);
confirmNewMeetingBtn.addEventListener('click', createNewMeeting);
cancelNewMeetingBtn.addEventListener('click', closeNewMeetingModal);
addBacklogItemBtn.addEventListener('click', addBacklogItem);
newBacklogItemInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') addBacklogItem();
});
saveMeetingBtn.addEventListener('click', saveMeeting);
deleteMeetingBtn.addEventListener('click', deleteMeeting);
meetingDate.addEventListener('change', (e) => {
    if (currentMeetingId) {
        meetings = meetings.map(m =>
            m.id === currentMeetingId ? {...m, date: e.target.value} : m
        );
        updateFirebase();
    }
});
notesField.addEventListener('change', (e) => {
    if (currentMeetingId) {
        meetings = meetings.map(m =>
            m.id === currentMeetingId ? {...m, notes: e.target.value} : m
        );
        updateFirebase();
    }
});
nextStepsField.addEventListener('change', (e) => {
    if (currentMeetingId) {
        meetings = meetings.map(m =>
            m.id === currentMeetingId ? {...m, nextSteps: e.target.value} : m
        );
        updateFirebase();
    }
});

// ============================================
// FUNCIONES - BACKLOG
// ============================================

async function addBacklogItem() {
    const text = newBacklogItemInput.value.trim();
    if (!text) return;

    try {
        await db.collection('backlog').add({
            text: text,
            order: backlogItems.length,
            createdAt: new Date().toISOString()
        });
        newBacklogItemInput.value = '';
    } catch (error) {
        console.error('Error adding backlog item:', error);
        alert('Error al agregar tema al backlog');
    }
}

async function deleteBacklogItem(itemId) {
    if (!confirm('¿Eliminar este tema del backlog?')) return;

    try {
        await db.collection('backlog').doc(itemId).delete();
    } catch (error) {
        console.error('Error deleting backlog item:', error);
    }
}

async function reorderBacklog(draggedId, targetId) {
    const draggedIndex = backlogItems.findIndex(b => b.id === draggedId);
    const targetIndex = backlogItems.findIndex(b => b.id === targetId);

    if (draggedIndex === -1 || targetIndex === -1 || draggedIndex === targetIndex) return;

    // Reordenar array localmente
    const draggedItem = backlogItems[draggedIndex];
    backlogItems.splice(draggedIndex, 1);
    backlogItems.splice(targetIndex, 0, draggedItem);

    // Renderizar inmediatamente para feedback visual
    renderBacklog();

    // Actualizar orden en Firebase en paralelo
    const updates = backlogItems.map((item, index) =>
        db.collection('backlog').doc(item.id).update({order: index})
    );

    Promise.all(updates).catch(err => {
        console.error('Error updating order:', err);
    });
}

function renderBacklog() {
    backlogList.innerHTML = backlogItems.map((item, index) => `
        <div class="backlog-item" draggable="true" data-backlog-id="${item.id}" data-index="${index}">
            <span class="backlog-item-icon"></span>
            <span class="backlog-item-text" style="flex: 1;">${escapeHtml(item.text)}</span>
            <button class="topic-delete" onclick="deleteBacklogItem('${item.id}')">×</button>
        </div>
    `).join('');

    setupBacklogDragListeners();
}

function setupBacklogDragListeners() {
    const items = document.querySelectorAll('.backlog-item');

    items.forEach((item, realIdx) => {
        const backlogItemId = item.dataset.backlogId;

        item.draggable = true;

        item.addEventListener('dragstart', (e) => {
            const backlogItem = backlogItems.find(b => b.id === backlogItemId);
            e.dataTransfer.effectAllowed = 'copyMove';
            e.dataTransfer.setData('text/plain', backlogItem ? backlogItem.text : backlogItemId);
            e.dataTransfer.setData('application/backlog-id', backlogItemId);
            setTimeout(() => item.classList.add('dragging'), 0);
        });

        item.addEventListener('dragend', () => {
            item.classList.remove('dragging');
            document.querySelectorAll('.backlog-item').forEach(i => {
                i.classList.remove('drag-over-above', 'drag-over-below');
            });
        });

        item.addEventListener('dragover', (e) => {
            const srcId = e.dataTransfer.getData('application/backlog-id');
            if (srcId === '' || srcId === backlogItemId) return;

            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';

            const rect = item.getBoundingClientRect();
            document.querySelectorAll('.backlog-item').forEach(i => {
                i.classList.remove('drag-over-above', 'drag-over-below');
            });

            item.classList.add(e.clientY < rect.top + rect.height / 2 ? 'drag-over-above' : 'drag-over-below');
        });

        item.addEventListener('dragleave', () => {
            item.classList.remove('drag-over-above', 'drag-over-below');
        });

        item.addEventListener('drop', (e) => {
            item.classList.remove('drag-over-above', 'drag-over-below');

            const srcId = e.dataTransfer.getData('application/backlog-id');
            if (srcId === '') return;

            e.preventDefault();
            e.stopPropagation();

            if (srcId === backlogItemId) return;

            // Encontrar índices actuales usando IDs
            const srcIdx = backlogItems.findIndex(b => b.id === srcId);
            const targetIdx = backlogItems.findIndex(b => b.id === backlogItemId);

            if (srcIdx === -1 || targetIdx === -1 || srcIdx === targetIdx) return;

            const rect = item.getBoundingClientRect();
            const insertBefore = e.clientY < rect.top + rect.height / 2;

            const [moved] = backlogItems.splice(srcIdx, 1);
            let finalIdx = srcIdx < targetIdx ? targetIdx - 1 : targetIdx;
            if (!insertBefore) finalIdx += 1;

            backlogItems.splice(finalIdx, 0, moved);

            // Actualizar orden en Firebase
            backlogItems.forEach((item, idx) => {
                db.collection('backlog').doc(item.id).update({ order: idx })
                    .catch(err => console.error('Error updating order:', err));
            });

            renderBacklog();
        });
    });
}

// ============================================
// FUNCIONES - REUNIONES
// ============================================

function openNewMeetingModal() {
    newMeetingDateInput.value = new Date().toISOString().split('T')[0];
    newMeetingModal.classList.remove('hidden');
}

function closeNewMeetingModal() {
    newMeetingModal.classList.add('hidden');
}

async function createNewMeeting() {
    const date = newMeetingDateInput.value;
    if (!date) {
        alert('Selecciona una fecha');
        return;
    }

    const newMeeting = {
        date: date,
        topicIds: [],
        notes: '',
        nextSteps: '',
        createdAt: new Date().toISOString()
    };

    try {
        const docRef = await db.collection('meetings').add(newMeeting);
        selectMeeting(docRef.id);
        closeNewMeetingModal();
    } catch (error) {
        console.error('Error creating meeting:', error);
        alert('Error al crear la reunión');
    }
}

function selectMeeting(meetingId) {
    currentMeetingId = meetingId;
    const meeting = meetings.find(m => m.id === meetingId);

    if (!meeting) return;

    emptyState.classList.add('hidden');
    meetingDetail.classList.remove('hidden');

    meetingDate.value = meeting.date;
    notesField.value = meeting.notes || '';
    nextStepsField.value = meeting.nextSteps || '';

    renderTopicsInMeeting();

    // Highlight active meeting
    document.querySelectorAll('.meeting-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-meeting-id="${meetingId}"]`)?.classList.add('active');
}

async function deleteMeeting() {
    if (!currentMeetingId) return;
    if (!confirm('¿Estás seguro de que quieres eliminar esta reunión?')) return;

    try {
        await db.collection('meetings').doc(currentMeetingId).delete();
        currentMeetingId = null;
        emptyState.classList.remove('hidden');
        meetingDetail.classList.add('hidden');
    } catch (error) {
        console.error('Error deleting meeting:', error);
        alert('Error al eliminar la reunión');
    }
}

function saveMeeting() {
    if (!currentMeetingId) return;
    updateFirebase();
    alert('Reunión guardada');
}

// ============================================
// FUNCIONES - TEMAS EN REUNIÓN
// ============================================

function addTopicToMeeting(backlogItemId) {
    if (!currentMeetingId) return;
    const meeting = meetings.find(m => m.id === currentMeetingId);
    if (!meeting) return;

    if (!meeting.topicIds.includes(backlogItemId)) {
        meeting.topicIds.push(backlogItemId);
        updateFirebase();
    }
}

function removeTopicFromMeeting(backlogItemId) {
    if (!currentMeetingId) return;
    const meeting = meetings.find(m => m.id === currentMeetingId);
    if (!meeting) return;

    meeting.topicIds = meeting.topicIds.filter(id => id !== backlogItemId);
    updateFirebase();
}

function toggleTopicCompleted(backlogItemId) {
    if (!currentMeetingId) return;
    const meeting = meetings.find(m => m.id === currentMeetingId);
    if (!meeting) return;

    if (!meeting.completedTopicIds) {
        meeting.completedTopicIds = [];
    }

    if (meeting.completedTopicIds.includes(backlogItemId)) {
        meeting.completedTopicIds = meeting.completedTopicIds.filter(id => id !== backlogItemId);
    } else {
        meeting.completedTopicIds.push(backlogItemId);
    }

    updateFirebase();
}

function renderTopicsInMeeting() {
    if (!currentMeetingId) return;
    const meeting = meetings.find(m => m.id === currentMeetingId);
    if (!meeting) return;

    const topicIds = meeting.topicIds || [];
    const topicElements = topicIds.map(topicId => {
        const backlogItem = backlogItems.find(b => b.id === topicId);

        // Si no encuentra el tema en backlog, lo busca en Firestore
        const topicText = backlogItem ? backlogItem.text : topicId;
        const isCompleted = meeting.completedTopicIds && meeting.completedTopicIds.includes(topicId);

        return `
            <div class="topic-item ${isCompleted ? 'completed' : ''}">
                <input type="checkbox" ${isCompleted ? 'checked' : ''}
                       onchange="toggleTopicCompleted('${topicId}')">
                <span class="topic-text">${escapeHtml(topicText)}</span>
                <button class="topic-delete" onclick="removeTopicFromMeeting('${topicId}')">×</button>
            </div>
        `;
    }).filter(el => el).join('');

    if (!topicElements) {
        topicsInMeeting.innerHTML = '<div style="text-align: center; color: var(--muted); font-size: 12px; flex: 1; display: flex; align-items: center; justify-content: center;">⬆️ Arrastra temas del backlog aquí</div>';
    } else {
        topicsInMeeting.innerHTML = topicElements;
    }

    // Setup drop zone
    setupDropZone();

    // Cargar datos de Firestore si falta algún tema
    topicIds.forEach(topicId => {
        const found = backlogItems.find(b => b.id === topicId);
        if (!found) {
            db.collection('backlog').doc(topicId).get().then(doc => {
                if (doc.exists) {
                    const newItem = {id: topicId, ...doc.data()};
                    backlogItems.push(newItem);
                    renderTopicsInMeeting(); // Re-render con los datos
                }
            });
        }
    });
}

function setupDropZone() {
    // DROP EN ZONA DE TEMAS
    topicsInMeeting.addEventListener('dragover', (e) => {
        if (e.dataTransfer.types.includes('application/backlog-id')) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            topicsInMeeting.classList.add('drag-over');
        }
    });

    topicsInMeeting.addEventListener('dragleave', () => {
        topicsInMeeting.classList.remove('drag-over');
    });

    topicsInMeeting.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        topicsInMeeting.classList.remove('drag-over');

        const backlogId = e.dataTransfer.getData('application/backlog-id');
        if (backlogId) {
            addTopicToMeeting(backlogId);
        }
    });

    // DROP EN NOTAS (usa text/plain que viene automático)
    notesDropContainer.addEventListener('dragover', (e) => {
        if (e.dataTransfer.types.includes('text/plain')) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            notesDropContainer.classList.add('drag-over');
        }
    });

    notesDropContainer.addEventListener('dragleave', () => {
        notesDropContainer.classList.remove('drag-over');
    });

    notesDropContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        notesDropContainer.classList.remove('drag-over');

        const text = e.dataTransfer.getData('text/plain').trim();
        if (text) {
            const bullet = `• ${text}`;
            notesField.value = notesField.value ? notesField.value + '\n' + bullet : bullet;
            notesField.dispatchEvent(new Event('change'));
            notesField.focus();
        }
    });
}

// ============================================
// FUNCIONES - RENDERIZADO
// ============================================

function renderMeetingsList() {
    meetingsList.innerHTML = meetings.map(meeting => `
        <div class="meeting-item ${meeting.id === currentMeetingId ? 'active' : ''}"
             data-meeting-id="${meeting.id}"
             onclick="selectMeeting('${meeting.id}')">
            <span class="meeting-item-date">${formatDate(meeting.date)}</span>
            <span class="meeting-item-count">${(meeting.topicIds || []).length} temas</span>
        </div>
    `).join('');
}

function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('es-ES', {
        day: 'numeric',
        month: 'short',
        year: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// FUNCIONES - FIREBASE
// ============================================

async function updateFirebase() {
    if (!currentMeetingId) return;
    const meeting = meetings.find(m => m.id === currentMeetingId);
    if (!meeting) return;

    try {
        await db.collection('meetings').doc(currentMeetingId).update({
            date: meeting.date,
            topicIds: meeting.topicIds,
            completedTopicIds: meeting.completedTopicIds || [],
            notes: meeting.notes,
            nextSteps: meeting.nextSteps,
            updatedAt: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error updating meeting:', error);
    }
}

function loadBacklog() {
    if (unsubscribeBacklog) unsubscribeBacklog();

    unsubscribeBacklog = db.collection('backlog')
        .orderBy('order', 'asc')
        .onSnapshot((snapshot) => {
            backlogItems = snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            }));
            renderBacklog();
        }, (error) => {
            console.error('Error loading backlog:', error);
            // Fallback a createdAt si order no existe
            db.collection('backlog')
                .orderBy('createdAt', 'desc')
                .onSnapshot((snapshot) => {
                    backlogItems = snapshot.docs.map(doc => ({
                        id: doc.id,
                        ...doc.data()
                    }));
                    renderBacklog();
                });
        });
}

function loadMeetings() {
    if (unsubscribeMeetings) unsubscribeMeetings();

    unsubscribeMeetings = db.collection('meetings')
        .orderBy('date', 'desc')
        .onSnapshot((snapshot) => {
            meetings = snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            }));
            renderMeetingsList();

            // Si hay reunión actual, actualizar su contenido
            if (currentMeetingId && meetings.find(m => m.id === currentMeetingId)) {
                renderTopicsInMeeting();
            }
        }, (error) => {
            console.error('Error loading meetings:', error);
            alert('Error al cargar las reuniones. Verifica tu conexión a internet.');
        });
}

// ============================================
// INICIALIZACIÓN
// ============================================

function init() {
    loadBacklog();
    loadMeetings();
}

init();
