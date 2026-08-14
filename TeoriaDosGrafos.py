import streamlit as st
import networkx as nx

st.set_page_config(
    page_title="Teoria dos Grafos",
    layout="wide"
)

editor = st.components.v2.component(
    name = "editor",
    
    html="""
    <div id="grafos">
    
        <div id="barra_lateral">
            <button id="criar_vertice"> Vértice </button>
            <button id="deletar"> Excluir selecionado </button>
        
            <span id="descricao"> Clique em dois vértices para criar uma aresta </span>
        </div>    
      
    <div id="cy"></div>
    
    </div>
    """,
    
    css="""
    #grafos {
        width: 100%;
        height: 600px;

        border: 1px solid #444;
        border-radius: 10px;

        overflow: hidden;

        background-color: #111827;

        font-family: sans-serif;
    }

    #barra_lateral {
        height: 50px;

        display: flex;
        align-items: center;

        gap: 10px;

        padding: 0 15px;

        background-color: #1f2937;

        border-bottom: 1px solid #374151;
    }

    button {
        border: none;

        border-radius: 6px;

        padding: 8px 14px;

        background-color: #2563eb;
        color: white;

        cursor: pointer;

        font-size: 14px;
    }

    button:hover {
        background-color: #1d4ed8;
    }

    #deletar {
        background-color: #dc2626;
    }

    #deletar:hover {
        background-color: #b91c1c;
    }

    #hint {
        margin-left: auto;

        color: #9ca3af;

        font-size: 13px;
    }

    #cy {
        width: 100%;
        height: calc(100% - 50px);
    }
    """,

    js="""
    export default function({
        parentElement,
        setStateValue
    }) {

        function loadCytoscape() {

            return new Promise((resolve, reject) => {

                if (window.cytoscape) {
                    resolve(window.cytoscape);
                    return;
                }

                const script = document.createElement("script");

                script.src =
                    "https://cdn.jsdelivr.net/npm/cytoscape@3.33.1/dist/cytoscape.min.js";

                script.onload = () => {
                    resolve(window.cytoscape);
                };

                script.onerror = () => {
                    reject(
                        new Error("Erro")
                    );
                };

                document.head.appendChild(script);
            });
        }

        let cy = null;

        function sendGraphToPython() {

            if (!cy) {
                return;
            }

            const nodes = cy.nodes().map(node => {

                const position = node.position();

                return {
                    id: node.id(),
                    label: node.data("label"),
                    x: position.x,
                    y: position.y
                };
            });


            const edges = cy.edges().map(edge => {

                return {
                    id: edge.id(),
                    source: edge.source().id(),
                    target: edge.target().id()
                };
            });


            setStateValue("graph", {
                nodes: nodes,
                edges: edges
            });
        }

        loadCytoscape()
            .then(cytoscape => {

                const container =
                    parentElement.querySelector("#cy");

                cy = cytoscape({
                    container: container,
                    elements: [],
                    style: [
                        {
                            selector: "node",
                            style: {
                                "background-color": "#2563eb",
                                "label": "data(label)",
                                "color": "#ffffff",
                                "text-valign": "center",
                                "text-halign": "center",
                                "font-size": "14px",
                                "width": 40,
                                "height": 40,
                                "border-width": 2,
                                "border-color": "#60a5fa"
                            }
                        },

                        {
                            selector: "node:selected",
                            style: {
                                "background-color": "#f59e0b",
                                "border-color": "#fbbf24",
                                "border-width": 3
                            }
                        },

                        {
                            selector: "edge",
                            style: {
                                "width": 3,
                                "line-color": "#9ca3af",
                                "curve-style": "bezier"
                            }
                        },

                        {
                            selector: "edge:selected",
                            style: {
                                "line-color": "#f59e0b",
                                "width": 5
                            }
                        }
                    ],

                    layout: {
                        name: "grid"
                    }
                });

                const addButton =
                    parentElement.querySelector("#criar_vertice");

                addButton.onclick = () => {

                    const count =
                        cy.nodes().length;

                    const id =
                        String.fromCharCode(
                            65 + count
                        );

                    const node =
                        cy.add({

                            group: "nodes",
                            data: {
                                id: id,
                                label: id
                            },

                            position: {
                                x: 100 + count * 70,
                                y: 150
                            }
                        });

                    node.select();

                    sendGraphToPython();
                };

                const deleteButton =
                    parentElement.querySelector(
                        "#deletar"
                    );

                deleteButton.onclick = () => {

                    cy.remove(
                        cy.$(":selected")
                    );

                    sendGraphToPython();
                };

                let firstNode = null;

                cy.on("tap", "node", event => {

                    const node =
                        event.target;

                    if (firstNode === null) {
                        firstNode = node;
                        node.select();
                        return;
                    }

                    if (firstNode.id() === node.id()) {
                        firstNode.unselect();
                        firstNode = null;
                        return;
                    }
                    
                    const source =
                        firstNode;

                    const target =
                        node;

                    const edgeId =
                        source.id()
                        + "-"
                        + target.id();

                    if (
                        cy.getElementById(edgeId).length === 0
                    ) {

                        cy.add({

                            group: "edges",
                            data: {
                                id: edgeId,
                                source: source.id(),
                                target: target.id()
                            }
                        });
                    }

                    source.unselect();

                    firstNode = null;

                    sendGraphToPython();
                });

                cy.on("remove", () => {
                    sendGraphToPython();

                });

                cy.on("dragfree", "node", () => {
                    sendGraphToPython();

                });

                sendGraphToPython();

            })

            .catch(error => {

                console.error(error);

            });

        return () => {

            if (cy) {
                cy.destroy();
                cy = null;
            }

        };
    }
    """
)

def criar_grafico(dados):
    
    G = nx.Graph()
    
    if not dados:
        return G
    
    for vertice in dados.get("nodes", []):
        G.add_node(vertice["id"])
        
    for aresta in dados.get("edges", []):
        G.add_edge(aresta["source"],
                   aresta["target"])
    
    return G

st.title("Grafo")

st.caption("Tela interativa para criação de Grafos")


st.sidebar.header("***Ferramentas***")

st.sidebar.markdown("""### **Como usar:**
**1.** Clique em '+ Vértice'

**2.** Arraste os vértices

**3.** Clique em dois vértices para criar uma aresta entre eles

**4.** Selecione um elemento e clique em 'Exluir elemento' para deletá-lo

""")

st.sidebar.divider()

st.sidebar.subheader("To-Do")

st.sidebar.checkbox("Arestas direcionadas", disabled=True)
st.sidebar.checkbox("Verificação de outros tipos de grafos", disabled=True)

resultado = editor(key="editor",
               default={
                   "graph" : {
                       "nodes" : [],
                       "edges" : []
                   }
               },
               on_graph_change=lambda: None,
               width="stretch",
               height=600
               )

dados = resultado.graph
G = criar_grafico(dados)

st.divider()

st.subheader("Análise do Grafo")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Vértices", G.number_of_nodes())
    
with col2:
    st.metric("Arestas", G.number_of_edges())
    
with col3:
    if G.number_of_edges() > 0:
        
        conectado = nx.is_connected(G)
        
        if conectado:
            sn = "Sim"
        else:
            sn = "Não"
        
        st.metric("Conexo", sn)
    else: 
        
        st.metric("Conexo", "-")

with col4:
    if G.number_of_nodes() > 0:
    
        grau = dict(G.degree())
        
        maior_grau = max(grau.values())
        
        st.metric("Maior grau", maior_grau)
    else:
        
        st.metric("Maior grau", "-")

st.subheader("Informações do Grafo")

# Grafo trivial
if G.number_of_nodes() == 1 and G.number_of_edges() == 0:
    st.metric("**Grafo Trivial**", "Sim") 
else:
    st.metric("**Grafo Trivial**", "Não") 

# Grafo ciclo
st.metric("**Grafo Ciclo**", "Não")
if G.number_of_nodes() > 0:
    if G.number_of_nodes() == G.number_of_edges():
        conectado = nx.is_connected(G)
        if conectado == 2:
            st.metric("**Grafo Ciclo**", "Sim")

with st.expander("Dados do Grafo"):
    st.json(dados)