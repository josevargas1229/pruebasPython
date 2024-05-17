import random

def _actualizar_velocidad(self):
    for i in range(self.NUMERO_POBLACION):
        for j in range(len(self._velocidad)):
            r1 = random.random()
            r2 = random.random()
            v2 = self.W*self._velocidad[i][j]+self.C1*r1*(self._pbest[i][j]-self._velocidad[i][j])+self.C2*r2*(self._gbest_c[j]-self._velocidad[i][j])
            self._velocidad[i][j]=v2
def _actualizar_poblacion(self):
    for i in range(self.NUMERO_POBLACION):
        for j in range(len(self._poblacion)):
            x2=self._poblacion[i][j]+self._velocidad[i][j]
            self._poblacion[i][j]=x2
