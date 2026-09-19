const API_BASE_URL = '/api';

document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const commentForm = document.getElementById('commentForm');
    
    if (uploadForm) {
        inicializarPaginaPrincipal();
    } else if (commentForm) {
        const urlParams = new URLSearchParams(window.location.search);
        const docId = urlParams.get('id');
        
        if (docId) {
            inicializarPaginaDocumento(docId);
        } else {
            alert('Identificador do documento não fornecido.');
            window.location.href = 'index.html';
        }
    }
});

// Página Principal

function inicializarPaginaPrincipal() {
    carregarDocumentos();
    configurarFormularioUpload();
}

async function carregarDocumentos() {
    const documentList = document.getElementById('documentList');
    
    try {
        const resposta = await fetch(`${API_BASE_URL}/documentos/`);
        
        if (!resposta.ok) {
            throw new Error('Falha ao obter os documentos da API.');
        }
        
        const documentos = await resposta.json();
        documentList.innerHTML = '';
        
        if (documentos.length === 0) {
            documentList.innerHTML = '<p>Nenhum documento registado no sistema.</p>';
            return;
        }

        documentos.forEach(doc => {
            const docElement = document.createElement('div');
            docElement.className = 'document-item';
            
            const dataFormatada = new Date(doc.data_upload.replace(' ', 'T') + 'Z').toLocaleString('pt-BR');
            
            docElement.innerHTML = `
                <div>
                    <strong>${doc.titulo}</strong>
                    <br>
                    <span class="date-text">${dataFormatada}</span>
                </div>
                <a href="documento.html?id=${doc.id}" class="button-link">Ver Detalhes</a>
            `;
            documentList.appendChild(docElement);
        });
    } catch (erro) {
        console.error(erro);
        documentList.innerHTML = '<p>Erro ao carregar a lista de documentos.</p>';
    }
}

function configurarFormularioUpload() {
    const form = document.getElementById('uploadForm');
    
    form.addEventListener('submit', async (evento) => {
        evento.preventDefault();
        
        const formData = new FormData(form);
        const botaoSubmit = form.querySelector('button[type="submit"]');
        
        botaoSubmit.disabled = true;
        botaoSubmit.textContent = 'A processar upload...';

        try {
            const resposta = await fetch(`${API_BASE_URL}/documentos/`, {
                method: 'POST',
                body: formData
            });

            if (!resposta.ok) {
                const erroData = await resposta.json();
                throw new Error(erroData.detail || 'Falha no servidor durante o upload.');
            }

            form.reset();
            carregarDocumentos();
        } catch (erro) {
            alert(`Erro na operação: ${erro.message}`);
        } finally {
            botaoSubmit.disabled = false;
            botaoSubmit.textContent = 'Enviar Documento';
        }
    });
}

// Página de Detalhes

function inicializarPaginaDocumento(docId) {
    carregarDetalhesDocumento(docId);
    carregarComentarios(docId);
    configurarFormularioComentario(docId);
}

async function carregarDetalhesDocumento(docId) {
    try {
        const resposta = await fetch(`${API_BASE_URL}/documentos/`);
        if (!resposta.ok) throw new Error('Falha ao carregar metadados da API.');
        
        const documentos = await resposta.json();
        const doc = documentos.find(d => d.id == docId);

        if (!doc) {
            alert('Documento não encontrado no servidor.');
            window.location.href = 'index.html';
            return;
        }

        document.getElementById('docTitle').textContent = doc.titulo;

        const descElement = document.getElementById('docDescricao');
        if (doc.descricao && doc.descricao.trim() !== "") {
            descElement.textContent = doc.descricao;
        } else {
            descElement.style.display = 'none';
}

        document.getElementById('docDate').textContent = new Date(doc.data_upload.replace(' ', 'T') + 'Z').toLocaleString('pt-BR');
        document.getElementById('downloadBtn').href = `${API_BASE_URL}/documentos/${docId}/download`;

    } catch (erro) {
        console.error(erro);
        document.getElementById('docTitle').textContent = 'Erro ao carregar informações';
    }
}

async function carregarComentarios(docId) {
    const commentList = document.getElementById('commentList');
    
    try {
        const resposta = await fetch(`${API_BASE_URL}/documentos/${docId}/comentarios`);
        if (!resposta.ok) throw new Error('Falha ao obter histórico de comentários.');
        
        const comentarios = await resposta.json();
        commentList.innerHTML = '';
        
        if (comentarios.length === 0) {
            commentList.innerHTML = '<p>Nenhum comentário registado para este documento.</p>';
            return;
        }

        comentarios.forEach(com => {
            const comElement = document.createElement('div');
            comElement.className = 'comment-item';
            
            const dataFormatada = new Date(com.data_hora_registro.replace(' ', 'T') + 'Z').toLocaleString('pt-BR');
            
            comElement.innerHTML = `
                <div class="comment-wrapper">
                    <p class="comment-text">${com.texto}</p>
                    <span class="date-text">${dataFormatada}</span>
                </div>
            `;

            commentList.appendChild(comElement);
        });
    } catch (erro) {
        console.error(erro);
        commentList.innerHTML = '<p>Erro crítico ao carregar comentários.</p>';
    }
}

function configurarFormularioComentario(docId) {
    const form = document.getElementById('commentForm');
    
    form.addEventListener('submit', async (evento) => {
        evento.preventDefault();
        
        const textoInput = document.getElementById('comentarioTexto');
        const botaoSubmit = form.querySelector('button[type="submit"]');
        
        botaoSubmit.disabled = true;
        botaoSubmit.textContent = 'A processar...';

        try {
            const resposta = await fetch(`${API_BASE_URL}/documentos/${docId}/comentarios`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ texto: textoInput.value })
            });

            if (!resposta.ok) {
                const erroData = await resposta.json();
                throw new Error(erroData.detail || 'Falha ao persistir o comentário.');
            }

            form.reset();
            carregarComentarios(docId);
        } catch (erro) {
            alert(`Erro na operação: ${erro.message}`);
        } finally {
            botaoSubmit.disabled = false;
            botaoSubmit.textContent = 'Adicionar Comentário';
        }
    });
}