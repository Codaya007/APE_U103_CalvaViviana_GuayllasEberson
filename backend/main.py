from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from afd import AutomataTransaccionBancaria, AutomataSmartLock, AutomataLogistica

app = FastAPI(title="API de Autómatas")

class EvalRequest(BaseModel):
    automata_type: str  # 'ecommerce', 'iot', 'genetica' para AFND, y 'transaccion', 'smartlock', 'logistica' para AFD
    sequence: List[str]

# Configuración de los 3 autómatas según diagramas
CONFIG = {
    "ecommerce": {
        "trans": {
            'q0': {'H': ['q1']},
            'q1': {'S': ['q2']},
            'q2': {'S': ['q2'], 'C': ['q3']},
            'q3': {}
        },
        "final": "q3"
    },
    "iot": {
        "trans": {
            'q0': {'H': ['q1']},
            'q1': {'T': ['q1'], 'U': ['q1'], 'C': ['q2']},
            'q2': {}
        },
        "final": "q2"
    },
    "genetica": {
        "trans": {
            'q0': {'K': ['q1']},
            'q1': {'G': ['q2']},
            'q2': {'X': ['q2'], 'F': ['q3']},
            'q3': {}
        },
        "final": "q3"
    }
}

@app.post("/evaluate")
async def evaluate(req: EvalRequest):
    cfg = CONFIG.get(req.automata_type)
    if not cfg: return {"error": "Tipo no válido"}

    current_states = {'q0'}
    history = [{"step": 0, "input": "Inicio", "states": list(current_states)}]

    for i, char in enumerate(req.sequence):
        next_states = set()
        for s in current_states:
            if s in cfg["trans"] and char in cfg["trans"][s]:
                for target in cfg["trans"][s][char]:
                    next_states.add(target)
        
        current_states = next_states
        # Lógica de q_error: si el conjunto de estados está vacío
        display_states = list(current_states) if current_states else ["q_error (Trampa)"]
        
        history.append({
            "step": i + 1,
            "input": char,
            "states": display_states
        })
        
        if not current_states: break

    return {
        "accepted": cfg["final"] in current_states,
        "history": history
    }

@app.post("/evaluate_dfa")
async def evaluate_dfa(req: EvalRequest):
    history = []
    accepted = False

    if req.automata_type == "transaccion":
        automata = AutomataTransaccionBancaria()
        history.append({"step": 0, "input": "Inicio", "states": [automata.estado_inicial]})
        res = automata.evaluar(req.sequence)
        accepted = (res == "Cadena aceptada")
        for i, h in enumerate(automata.historial):
            history.append({
                "step": i + 1,
                "input": h["evento"],
                "states": [h["a"]]
            })

    elif req.automata_type == "smartlock":
        automata = AutomataSmartLock()
        history.append({"step": 0, "input": "Inicio", "states": [automata.estado_actual]})
        for i, event in enumerate(req.sequence):
            automata.procesar_intento(event)
            history.append({
                "step": i + 1,
                "input": event,
                "states": [automata.estado_actual]
            })
            if automata.estado_actual == "q_block":
                break
        accepted = (automata.estado_actual == "q_open")

    elif req.automata_type == "logistica":
        automata = AutomataLogistica()
        history.append({"step": 0, "input": "Inicio", "states": [automata.estados[automata.estado_inicial]]})
        res = automata.procesar_flujo(req.sequence)
        accepted = ("Válido" in res)
        for i, h in enumerate(automata.historial):
            history.append({
                "step": i + 1,
                "input": h["evento"],
                "states": [h["destino"]]
            })
    else:
        return {"error": "Tipo no válido"}

    return {
        "accepted": accepted,
        "history": history
    }