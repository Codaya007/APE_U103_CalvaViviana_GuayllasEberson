class AutomataTransaccionBancaria:
    def __init__(self):
        self.estado_actual = "q0"
        self.estado_inicial = "q0"
        self.estado_final = "q_com"
        
        # Definición del DFA
        self.transiciones = {
            "q0": {"A": "q_aut"},
            "q_aut": {"C": "q_cap"},
            "q_cap": {"L": "q_com"},
            "q_com": {}, 
            "q_err": {} 
        }
        self.historial = []

    def evaluar_siguiente_estado(self, evento):
        # Buscamos el destino en la tabla de transiciones
        estado_siguiente = self.transiciones.get(self.estado_actual, {}).get(evento, "q_err")
        
        self.historial.append({
            "de": self.estado_actual,
            "evento": evento,
            "a": estado_siguiente
        })
        
        # ¡IMPORTANTE! Actualizamos el estado actual del autómata
        self.estado_actual = estado_siguiente
        return self.estado_actual

    def evaluar(self, eventos):
        self.estado_actual = self.estado_inicial
        self.historial = [] # Limpiamos historial para una nueva evaluación

        for evento in eventos:
            self.evaluar_siguiente_estado(evento)
            if self.estado_actual == "q_err": # Optimización: si cae en error, para qué seguir
                break
        
        return "Cadena aceptada" if self.estado_actual == self.estado_final else "Cadena rechazada"

    def __str__(self):
        # Mejoramos el formato visual para que coincida con tu ejemplo
        pasos = [f"{h['de']} -({h['evento']})-> {h['a']}" for h in self.historial]
        return " | ".join(pasos)


class AutomataSmartLock:
    def __init__(self):
        self.estados = {
            "q0": "Inicio", 
            "q1": "Primer intento fallido", 
            "q2": "Segundo intento fallido", 
            "q_block": "Bloqueado", 
            "q_open": "Abierto"
        }
        self.estado_actual = "q0"
        self.historial = []
        
        # Definición formal de la función de transición δ(q, σ)
        self.transiciones = {
            "q0": {"ok": "q_open", "bad": "q1"},
            "q1": {"ok": "q_open", "bad": "q2"},
            "q2": {"ok": "q_open", "bad": "q_block"},
            "q_block": {"bad": "q_block", "ok": "q_block"},
            "q_open": {} # Estado final, usualmente no procesa más
        }

    def procesar_intento(self, tipo):
        # 1. Si ya está abierto o bloqueado, manejamos el estado actual
        if self.estado_actual == "q_block":
            return "SISTEMA BLOQUEADO"
        if self.estado_actual == "q_open":
            return "LA PUERTA YA ESTÁ ABIERTA"

        # 2. Validar si el evento existe en el alfabeto para el estado actual
        proximo_estado = self.transiciones[self.estado_actual].get(tipo)

        if proximo_estado:
            # Guardamos en el historial antes de cambiar
            self.historial.append({
                "de": self.estado_actual,
                "evento": tipo,
                "a": proximo_estado
            })
            self.estado_actual = proximo_estado
            return f"Estado: {self.estados[self.estado_actual]}"
        else:
            # Si el evento no es válido (ej. envían algo que no es 'ok' o 'bad')
            return "ENTRADA NO RECONOCIDA"

    def __str__(self):
        s = ""
        for evento in self.historial:
            s += f"{evento['de']} -({evento['evento']})-> {evento['a']}\n"
        return s


class AutomataLogistica:
    def __init__(self):
        # Definición de los estados según el problema
        self.estados = {
            "q_cre": "CREADO",
            "q_emp": "EMPAQUETADO",
            "q_env": "ENVIADO",
            "q_ent": "ENTREGADO",
            "q_dev": "DEVUELTO",
            "q_can": "CANCELADO",
            "q_err": "ERROR_LOGISTICO"
        }
        
        self.estado_inicial = "q_cre"
        self.estado_actual = "q_cre"
        
        # Estados donde el proceso termina correctamente
        self.estados_finales = ["q_ent", "q_can", "q_dev"]
        
        # Diccionario de transiciones (δ)
        self.transiciones = {
            "q_cre": {
                "emp": "q_emp", 
                "can": "q_can"
            },
            "q_emp": {
                "env": "q_env", 
                "can": "q_can"
            },
            "q_env": {
                "ent": "q_ent"
            },
            "q_ent": {
                "dev": "q_dev"
            },
            "q_can": {}, # Estado de parada
            "q_dev": {}, # Estado de parada
            "q_err": {}  # Estado trampa
        }
        self.historial = []

    def evaluar_paso(self, evento):
        # Buscamos la transición en el estado actual
        proximo = self.transiciones.get(self.estado_actual, {}).get(evento, "q_err")
        
        self.historial.append({
            "origen": self.estados[self.estado_actual],
            "evento": evento,
            "destino": self.estados[proximo]
        })
        
        self.estado_actual = proximo
        return self.estado_actual

    def procesar_flujo(self, secuencia_eventos):
        self.estado_actual = self.estado_inicial
        self.historial = []
        
        for evento in secuencia_eventos:
            self.evaluar_paso(evento)
            if self.estado_actual == "q_err":
                break
        
        es_valido = self.estado_actual in self.estados_finales
        return "Flujo Logístico Válido" if es_valido else "Flujo Logístico Inválido"

    def __str__(self):
        res = "TRAZA LOGÍSTICA:\n"
        for h in self.historial:
            res += f"[{h['origen']}] --({h['evento']})--> [{h['destino']}]\n"
        return res