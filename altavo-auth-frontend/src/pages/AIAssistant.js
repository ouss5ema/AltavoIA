import React, { useContext, useState, useRef, useEffect } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import api from '../api/axios'; // API pour le backend d'authentification/conversation (Flask)
import ai_api from '../api/ai_axios'; // API pour le backend RAG (FastAPI)
import "../App.css";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import Swal from 'sweetalert2';
import withReactContent from 'sweetalert2-react-content';
import { FaChevronDown, FaChevronRight } from 'react-icons/fa';
import { FiStar, FiShare2 } from 'react-icons/fi';

const MySwal = withReactContent(Swal);

// Icônes
const PlusIcon = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>;
const MessageSquareIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>;
const CopyIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>;
const UploadCloudIcon = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 17.2a4.6 4.6 0 0 0-4.5-5.2H12A5.4 5.4 0 0 0 7 17a4.6 4.6 0 0 0-4.5 4.9h19.1a4.6 4.6 0 0 0-1.6-9.7z"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>;
const SidebarCollapseIcon = ({isCollapsed}) => <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5m14 0l-4-4m4 4l-4 4"/></svg>;
const PaperclipIcon = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>;
const SparklesIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3L9.27 9.27L3 12l6.27 2.73L12 21l2.73-6.27L21 12l-6.27-2.73L12 3z"/></svg>;
const SendIcon = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>;
const MoreHorizontalIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="1"></circle><circle cx="19" cy="12" r="1"></circle><circle cx="5" cy="12" r="1"></circle></svg>;
const TrashIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>;
const EditIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>;
const PinIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="17" x2="12" y2="22"></line><path d="M17 3l-5 5-5-5h10z"></path><path d="M12 8v9"></path></svg>;
const UnpinIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 17v5"/><path d="M17 3l-5 5-5-5h10z"/><path d="M12 8v9"/><path d="M2 8l1.3 1.3a1 1 0 0 0 1.4 0L6 8"/></svg>;
const FileIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>;
const SpinnerIcon = () => <svg className="spinner-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>;

// Chevron icons inline (si react-icons non dispo)
const ChevronDownIcon = () => (
  <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 8 10 12 14 8"/></svg>
);
const ChevronRightIcon = () => (
  <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="8 6 12 10 8 14"/></svg>
);

// --- Composant pour les blocs de code ---
const CodeBlock = ({ language, code }) => {
    const [copySuccess, setCopySuccess] = useState('');

    const handleCopy = () => {
        navigator.clipboard.writeText(code).then(() => {
            setCopySuccess('Copié !');
            setTimeout(() => setCopySuccess(''), 2000);
        }, () => {
            setCopySuccess('Erreur');
        });
    };

    return (
        <div className="code-block-wrapper">
            <div className="code-block-header">
                <span>{language || 'code'}</span>
                <button onClick={handleCopy} className="copy-btn">
                    {copySuccess || <><CopyIcon /> Copier</>}
                </button>
            </div>
            <SyntaxHighlighter
                language={language}
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: '0 0 8px 8px' }}
                codeTagProps={{ style: { fontFamily: 'Consolas, "Courier New", monospace' } }}
            >
                {String(code).replace(/\n$/, '')}
            </SyntaxHighlighter>
        </div>
    );
};

// --- Fonction pour parser le contenu des messages ---
const renderMessageContent = (content) => {
    const codeBlockRegex = /```(\w*?)\n([\s\S]+?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(content)) !== null) {
        if (match.index > lastIndex) {
            parts.push({ type: 'text', value: content.substring(lastIndex, match.index) });
        }
        parts.push({ type: 'code', language: match[1], value: match[2] });
        lastIndex = match.index + match[0].length;
    }

    if (lastIndex < content.length) {
        parts.push({ type: 'text', value: content.substring(lastIndex) });
    }
    
    if (parts.length === 0) return content;

    return parts.map((part, index) => {
        if (part.type === 'code') {
            return <CodeBlock key={index} language={part.language} code={part.value} />;
        }
        return <span key={index}>{part.value}</span>;
    });
};

// Nouvelle icône d'upload plus indicative
const UploadFileIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2.5" fill="#23589C"/><path d="M12 16V8" stroke="#fff" strokeWidth="2" strokeLinecap="round"/><path d="M8.5 11.5L12 8l3.5 3.5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
);

export default function AIAssistant() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  // États du chat
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);
  
  // États des conversations
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [loadingConversations, setLoadingConversations] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [openedMenuId, setOpenedMenuId] = useState(null); // Pour gérer le menu contextuel
  const [renamingId, setRenamingId] = useState(null); // Pour gérer le renommage
  const [tempTitle, setTempTitle] = useState(""); // Pour stocker le titre pendant le renommage
  const renameInputRef = useRef(null);
  const [conversationsOpen, setConversationsOpen] = useState(true);
  const [showAllConversations, setShowAllConversations] = useState(false);

  // États de l'upload
  const [uploading, setUploading] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [uploadError, setUploadError] = useState("");
  const fileInputRef = useRef();

  // États de streaming
  const [isStreaming, setIsStreaming] = useState(false);

  // Ajout de l'état pour l'épinglage (exemple, à adapter selon ta logique)
  const [isPinned, setIsPinned] = useState(false);

  const mainContentRef = useRef(null);

  // --- EFFETS ---

  // Redirection si non connecté
  useEffect(() => {
    if (!user) navigate("/connexion");
  }, [user, navigate]);

  // Scroll automatique du chat
  useEffect(() => {
    const chatScrollable = document.querySelector('.chat-scrollable');
    if (!chatScrollable) return;
    const isNearBottom = () => {
      const threshold = 120;
      return chatScrollable.scrollHeight - chatScrollable.scrollTop - chatScrollable.clientHeight < threshold;
    };
    if (isNearBottom()) {
      chatScrollable.scrollTo({ top: chatScrollable.scrollHeight, behavior: "smooth" });
    }
  }, [messages]);

  // Chargement initial des conversations et documents
  useEffect(() => {
    if(user) {
      fetchConversations();
      fetchDocuments();
    }
  }, [user]);

  // CLose menu on click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (openedMenuId && !event.target.closest('.conversation-item-actions')) {
        setOpenedMenuId(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [openedMenuId]);

  // Focus input when renaming
  useEffect(() => {
    if (renamingId && renameInputRef.current) {
      renameInputRef.current.focus();
      renameInputRef.current.select();
    }
  }, [renamingId]);

  // --- GESTION DES CONVERSATIONS ---

  const fetchConversations = async () => {
    setLoadingConversations(true);
    try {
      const { data } = await api.get('/conversations/');
      setConversations(data);
    } catch (err) {
      console.error("Erreur fetchConversations:", err);
    } finally {
      setLoadingConversations(false);
    }
  };
  
  const handleSelectConversation = async (convId) => {
    if (convId === activeConversationId) return;
    setActiveConversationId(convId);
    setLoading(true);
    setMessages([]);
    try {
      const { data } = await api.get(`/conversations/${convId}/messages`);
      const formattedMessages = data.map(msg => ({
        role: msg.sender,
        content: msg.content,
      }));
      setMessages(formattedMessages);
    } catch (err) {
      setMessages([{ role: 'assistant', content: 'Erreur lors du chargement des messages.', mode: 'error' }]);
    }
    setLoading(false);
  };
  
  const handleNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
    setInput("");
  };

  const saveConversation = async (userMessage, aiMessage) => {
    try {
      if (activeConversationId) {
        // Ajouter les messages à la conversation existante
        await api.post(`/conversations/${activeConversationId}/messages`, {
          user_message: userMessage,
          ai_response: aiMessage,
        });
      } else {
        // Créer une nouvelle conversation
        const { data: newConv } = await api.post('/conversations/', {
          message: userMessage,
          ai_response: aiMessage,
        });
        setActiveConversationId(newConv.id);
        setConversations(prev => [newConv, ...prev]);
      }
    } catch (error) {
      console.error("Erreur lors de la sauvegarde:", error);
      // Afficher une erreur non bloquante à l'utilisateur
    }
  };

  const handleStartRename = (conv) => {
    setRenamingId(conv.id);
    setTempTitle(conv.title);
    setOpenedMenuId(null); // Fermer le menu
  };

  const handleRename = async (convId) => {
    if (!tempTitle.trim()) {
      setRenamingId(null); // Annuler si le titre est vide
      return;
    }
    try {
      const { data: updatedConv } = await api.put(`/conversations/${convId}/rename`, { title: tempTitle });
      setConversations(prev => prev.map(c => c.id === convId ? updatedConv : c));
    } catch (error) {
      console.error("Erreur lors du renommage:", error);
      alert("Impossible de renommer la conversation.");
    } finally {
      setRenamingId(null);
    }
  };

  const handlePinConversation = () => {
    setIsPinned((prev) => !prev);
    // TODO: Appeler l'API pour épingler/désépingler si besoin
  };

  const handleDeleteConversation = async (convId) => {
    Swal.fire({
      title: 'Êtes-vous sûr ?',
      text: "Cette conversation sera supprimée définitivement.",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Oui, supprimer !',
      cancelButtonText: 'Annuler'
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          await api.delete(`/conversations/${convId}`);
          setConversations(conversations.filter(c => c.id !== convId));
          if (activeConversationId === convId) setActiveConversationId(null);
          Swal.fire('Supprimé !', 'La conversation a été supprimée.', 'success');
        } catch (err) {
          Swal.fire('Erreur', "La suppression a échoué.", 'error');
        }
      }
    });
  };

  // --- GESTION DU CHAT ---

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    const userMessageContent = input.trim();
    if (!userMessageContent || loading || isStreaming) return;

    const userMessage = { role: "user", content: userMessageContent };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setLoading(true);
    setIsStreaming(true);
    
    try {
        const historyForApi = messages.map(msg => [msg.role, msg.content]);
        
        // Créer le message assistant initial
        const aiMessage = { role: "assistant", content: "" };
        setMessages([...newMessages, aiMessage]);

        // Faire la requête fetch avec streaming
        const response = await fetch(`${ai_api.defaults.baseURL}/ask`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: userMessageContent,
                history: historyForApi
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = "";
        let currentMode = "fallback";
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            
            // Traiter les lignes complètes
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Garder la dernière ligne incomplète dans le buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const jsonStr = line.slice(6).trim();
                        console.log("Received SSE line:", jsonStr); // Debug
                        if (jsonStr) {
                            const data = JSON.parse(jsonStr);
                            console.log("Parsed data:", data); // Debug
                            
                            switch (data.type) {
                                case 'mode':
                                    currentMode = data.value;
                                    console.log("Mode set to:", currentMode); // Debug
                                    break;
                                case 'token':
                                    fullResponse += data.value;
                                    console.log("Token received:", data.value); // Debug
                                    // Mettre à jour le contenu du message en temps réel
                                    setMessages(prev => {
                                        const updated = [...prev];
                                        const lastMessage = updated[updated.length - 1];
                                        if (lastMessage && lastMessage.role === 'assistant') {
                                            lastMessage.content = fullResponse;
                                            lastMessage.mode = currentMode;
                                        }
                                        return updated;
                                    });
                                    break;
                                case 'done':
                                    fullResponse = data.full_response;
                                    console.log("Stream completed, full response:", fullResponse); // Debug
                                    // Message final
                                    setMessages(prev => {
                                        const updated = [...prev];
                                        const lastMessage = updated[updated.length - 1];
                                        if (lastMessage && lastMessage.role === 'assistant') {
                                            lastMessage.content = fullResponse;
                                            lastMessage.mode = currentMode;
                                        }
                                        return updated;
                                    });
                                    break;
                            }
                        }
                    } catch (error) {
                        console.error("Erreur parsing SSE:", error, "Line:", line);
                    }
                }
            }
        }

        // Sauvegarder la conversation une fois terminée
        if (fullResponse) {
            saveConversation(userMessageContent, fullResponse);
        }

    } catch (error) {
        console.error("Erreur lors de l'envoi du message:", error);
        const errorMessage = {
            role: "assistant",
            content: "Désolé, une erreur est survenue lors de l'appel à l'IA.",
            mode: 'error'
        };
        setMessages([...newMessages, errorMessage]);
    } finally {
        setLoading(false);
        setIsStreaming(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    // On laisse l'utilisateur valider l'envoi
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // Optionnel: afficher une petite notification "Copié !"
  }

  // --- GESTION DES DOCUMENTS (UPLOAD/LISTING) ---

  const fetchDocuments = async () => {
    try {
      // Utiliser ai_api pour appeler le backend FastAPI
      const { data } = await ai_api.get("/documents");
      setUploadedDocs(data.files || []);
    } catch (error) {
      console.error("Erreur lors de la récupération des documents:", error);
      // Gérer l'erreur 401 ou autre
      if (error.response && error.response.status === 401) {
          setUploadError("Session expirée. Veuillez vous reconnecter.");
      } else {
          setUploadError("Impossible de charger les documents.");
      }
    }
  };

  const handleDeleteDocument = (docId, docName) => {
    MySwal.fire({
      title: 'Êtes-vous sûr ?',
      html: `Voulez-vous vraiment supprimer le fichier <strong>${docName}</strong> ?<br/>Cette action est irréversible.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#c0392b',
      cancelButtonColor: '#3498db',
      confirmButtonText: 'Oui, supprimer !',
      cancelButtonText: 'Annuler',
      background: '#fff',
      customClass: {
        title: 'swal-title',
        popup: 'swal-popup',
        confirmButton: 'swal-confirm-btn',
        cancelButton: 'swal-cancel-btn'
      }
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          await ai_api.delete(`/documents/${docId}`);
          setUploadedDocs(prevDocs => prevDocs.filter(doc => doc.id !== docId));
          MySwal.fire(
            'Supprimé !',
            `Le fichier ${docName} a été supprimé.`,
            'success'
          );
        } catch (error) {
          console.error("Erreur lors de la suppression du document:", error);
          MySwal.fire(
            'Erreur !',
            "Impossible de supprimer le document.",
            'error'
          );
        }
      }
    });
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    handleUpload(selectedFiles);
  };

  const handleUpload = async (filesToUpload) => {
    if (filesToUpload.length === 0) return;

    const formData = new FormData();
    filesToUpload.forEach((file) => {
      formData.append("files", file);
    });

    setUploading(true);
    setUploadError("");

    try {
      // Utiliser ai_api pour l'upload
      const { data } = await ai_api.post("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      // Mettre à jour la liste des documents après un upload réussi
      if (data.success) {
        fetchDocuments(); 
      }
    } catch (error) {
      console.error("Erreur d'upload:", error);
      if (error.response) {
        // Gérer spécifiquement l'erreur de conflit (fichier existant)
        if (error.response.status === 409) {
          setUploadError(`Ce fichier existe déjà. Veuillez le supprimer d'abord si vous souhaitez le remplacer.`);
        } else if (error.response.data && error.response.data.detail) {
          // Gérer les autres erreurs structurées du backend
          setUploadError(`Erreur: ${error.response.data.detail}`);
        } else {
          // Gérer les autres erreurs HTTP
          setUploadError("Une erreur est survenue lors de l'upload.");
        }
      } else {
        // Gérer les erreurs réseau (pas de réponse du serveur)
        setUploadError("Erreur réseau. Impossible de joindre le serveur.");
      }
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setFiles(Array.from(e.dataTransfer.files));
    setUploadError("");
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  // Fonction pour partager la conversation (copier le lien)
  const handleShareConversation = () => {
    navigator.clipboard.writeText(window.location.href);
    Swal.fire({
      icon: 'success',
      title: 'Lien copié !',
      text: 'Le lien de la discussion a été copié dans le presse-papiers.',
      timer: 1500,
      showConfirmButton: false
    });
  };

  // --- RENDER ---
  
  if (!user) {
    return null; // Ou un spinner de chargement global
  }

  const WelcomeScreen = () => (
    <div className="welcome-screen">
      <img src="/logo-altavo.png" alt="Altavo Logo" className="welcome-logo" />
      <h1 className="welcome-title">Bienvenue sur Altavo IA</h1>
      <div className="suggestion-chips">
          <button onClick={() => handleSuggestionClick('Rédige un e-mail professionnel pour ')}><SparklesIcon /> Rédiger un e-mail</button>
          <button onClick={() => handleSuggestionClick('Explique le concept de ')}><SparklesIcon /> Expliquer un concept</button>
          <button onClick={() => handleSuggestionClick('Donne-moi 5 idées de titres pour un article sur ')}><SparklesIcon /> Brainstormer des idées</button>
      </div>
    </div>
  );

  return (
    <div className={`ai-container ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      {/* --- Barre Latérale --- */}
      <aside className="ai-sidebar">
        <div>
          <header className="sidebar-header">
            <img src="/logo-altavo.png" alt="Altavo Logo" className="sidebar-main-logo" />
            <button onClick={() => setSidebarCollapsed(!sidebarCollapsed)} className="sidebar-collapse-btn" title={sidebarCollapsed ? "Agrandir" : "Réduire"}>
                <SidebarCollapseIcon isCollapsed={sidebarCollapsed} />
            </button>
          </header>
          <div className="sidebar-top">
            <button className="sidebar-new-chat" onClick={handleNewConversation}>
              <PlusIcon /> <span>Nouvelle Discussion</span>
            </button>
            <nav className="sidebar-history">
              <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
                <h3 className="history-title">Récent</h3>
                <button
                  className="dropdown-toggle-btn"
                  onClick={() => setConversationsOpen(v => !v)}
                  style={{background: 'none', border: 'none', cursor: 'pointer', padding: 2, marginLeft: 4}}
                  aria-label={conversationsOpen ? 'Réduire la liste' : 'Déplier la liste'}
                >
                  {conversationsOpen ? <ChevronDownIcon /> : <ChevronRightIcon />}
                </button>
              </div>
              {conversationsOpen && (loadingConversations ? <div className="sidebar-loader">Chargement...</div> : (
                <ul>
                  {(showAllConversations ? conversations : conversations.slice(0, 5)).map(conv => (
                    <li key={conv.id} className="conversation-item">
                      <div className="conversation-link-wrapper">
                        {renamingId === conv.id ? (
                          <input
                            ref={renameInputRef}
                            type="text"
                            value={tempTitle}
                            onChange={(e) => setTempTitle(e.target.value)}
                            onBlur={() => handleRename(conv.id)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') handleRename(conv.id);
                              if (e.key === 'Escape') setRenamingId(null);
                            }}
                            className="rename-input"
                          />
                        ) : (
                          <a href="#" className={`${conv.id === activeConversationId ? 'active' : ''} ${conv.is_pinned ? 'pinned' : ''}`} onClick={(e) => {e.preventDefault(); handleSelectConversation(conv.id)}}>
                            <MessageSquareIcon />
                            <span>{conv.title}</span>
                          </a>
                        )}
                      </div>
                      <div className="conversation-item-actions">
                        <button onClick={() => setOpenedMenuId(openedMenuId === conv.id ? null : conv.id)} className="more-btn">
                          <MoreHorizontalIcon />
                        </button>
                        {openedMenuId === conv.id && (
                          <div className="actions-menu">
                            <button className="menu-item" onClick={() => handlePinConversation(conv)}>
                              {conv.is_pinned ? <UnpinIcon /> : <PinIcon />}
                              {conv.is_pinned ? 'Désépingler' : 'Épingler'}
                            </button>
                            <button className="menu-item" onClick={() => handleStartRename(conv)}><EditIcon /> Renommer</button>
                            <button className="menu-item menu-item-danger" onClick={() => handleDeleteConversation(conv.id)}>
                              <TrashIcon /> Supprimer
                            </button>
                          </div>
                        )}
                      </div>
                    </li>
                  ))}
                  {conversations.length > 5 && !showAllConversations && (
                    <li style={{textAlign: 'center', marginTop: 8}}>
                      <button
                        onClick={() => setShowAllConversations(true)}
                        style={{
                          background: 'linear-gradient(90deg, #23589C 0%, #3b82f6 100%)',
                          color: '#fff',
                          border: 'none',
                          borderRadius: 20,
                          padding: '6px 18px',
                          fontWeight: 500,
                          cursor: 'pointer',
                          boxShadow: '0 2px 8px rgba(35,88,156,0.08)',
                          transition: 'background 0.2s',
                        }}
                      >
                        Voir plus
                      </button>
                    </li>
                  )}
                </ul>
              ))}
            </nav>
          </div>
        </div>
        <div className="sidebar-bottom">
           <div className="knowledge-base-section">
                <h3 className="knowledge-base-title">Base de connaissances</h3>
                <div className="knowledge-base-content">
                  {uploadedDocs.length > 0 ? (
                    <ul className="doc-list">
                      {uploadedDocs.map((doc) => (
                        <li key={doc.id} className="doc-item">
                          <div className="doc-item-icon"><FileIcon /></div>
                          <span className="doc-item-name">{doc.filename}</span>
                          <button 
                            className="doc-item-delete-btn"
                            onClick={() => handleDeleteDocument(doc.id, doc.filename)}
                            title={`Supprimer ${doc.filename}`}
                          >
                            <TrashIcon />
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>Aucun document dans la base de connaissances.</p>
                  )}
                </div>
                 <div className="knowledge-upload-wrapper">
                    <label htmlFor="knowledge-file-input" className={`knowledge-upload-btn ${uploading ? 'disabled' : ''}`} aria-label="Uploader un fichier dans la base de connaissances">
                      {uploading ? (
                        <>
                          <SpinnerIcon />
                          <span>Chargement...</span>
                        </>
                      ) : (
                        <>
                          <UploadFileIcon />
                          <span>Uploader un Fichier</span>
                        </>
                      )}
                    </label>
                    <input
                      id="knowledge-file-input"
                      type="file"
                      multiple
                      onChange={handleFileChange}
                      ref={fileInputRef}
                      style={{ display: "none" }}
                      disabled={uploading}
                      accept=".pdf,.txt"
                    />
                    {uploadError && <div className="upload-error-msg">{uploadError}</div>}
                </div>
           </div>
          <div className="sidebar-footer">
            <div className="sidebar-user-info">
              <span className="sidebar-avatar">{user.username?.charAt(0).toUpperCase()}</span>
              <span>{user.username}</span>
            </div>
            <button className="sidebar-logout" onClick={logout} title="Déconnexion">
              <svg width="20" height="20" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4m7 14l5-5l-5-5m5 5H9"/></svg>
            </button>
          </div>
        </div>
      </aside>

      {/* --- Contenu Principal (Chat) --- */}
      <main className="ai-main-content" ref={mainContentRef}>
        <header className="main-header">
          <h1 className="main-header-title">
            {activeConversationId ? conversations.find(c => c.id === activeConversationId)?.title : 'Altavo IA'}
          </h1>
          <div className="main-header-actions">
            <button className="icon-btn" title={isPinned ? "Désépingler" : "Épingler"} onClick={handlePinConversation}>
              <FiStar size={22} color={isPinned ? '#fbbf24' : '#9ca3af'} fill={isPinned ? '#fbbf24' : 'none'} />
            </button>
            <button className="icon-btn" title="Partager la discussion" onClick={handleShareConversation}>
              <FiShare2 size={22} color="#2563eb" />
            </button>
            <span className="sidebar-avatar">{user.username?.charAt(0).toUpperCase()}</span>
          </div>
        </header>

        <div className="chat-scrollable">
          <div className="messages-list">
            {messages.length === 0 && !activeConversationId ? <WelcomeScreen /> : (
              messages.map((msg, idx) => (
                <div key={idx} className={`msg-wrapper msg-${msg.role}`}>
                  <div className="msg-bubble">
                    <div className="msg-content">
                      {renderMessageContent(msg.content)}
                      {isStreaming && idx === messages.length - 1 && <span className="blinking-cursor" />}
                    </div>
                    {msg.role === 'assistant' && !msg.mode?.includes('info') && (
                      <div className="msg-actions">
                        {msg.mode && <span className={`badge badge-${msg.mode}`}>{msg.mode}</span>}
                        <button onClick={() => copyToClipboard(msg.content)} className="action-btn" title="Copier"><CopyIcon /></button>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
          <div ref={chatEndRef} />
        </div>

        <div className="chat-input-area">
          <form className="chat-input-form" onSubmit={handleSend}>
            <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileChange}
                style={{ display: "none" }}
            />
            <button type="button" className="chat-attach-btn" onClick={() => fileInputRef.current?.click()} title="Joindre un document">
                <PaperclipIcon />
            </button>
            <input
              className="chat-input"
              type="text"
              placeholder="Envoyer un message à Altavo IA..."
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={loading}
              autoFocus
            />
            <button className="chat-send-btn" type="submit" disabled={loading || !input.trim()}>
              <SendIcon />
            </button>
          </form>
          <p className="input-footer-note">Altavo IA peut commettre des erreurs. Pensez à vérifier les informations importantes.</p>
        </div>
      </main>
    </div>
  );
} 