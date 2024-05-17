class Fraccion:
    def __init__ (self, num=0, den=1) -> None:
        if isinstance (num, int):
            self.num = num
        else:
            self.num=0
        if isinstance(den, int) and den!=0:
            self.den = den
        else:
            self.den=1
            
    # def __del__(self):
    #     print(f"Destruyendo la fraccion {self.num}/{self.den}")
    
    def __str__(self):
        return f"[{self.num}/{self.den}]"
    
    def __mul__(self, obj):
        n = self.num * obj.num
        d = self.den * obj.den
        r = Fraccion(n,d)
        return r
    
    def __add__(self, obj):
        n = self.num * obj.den + self.den * obj.num
        d = self.den * obj.den
        r = Fraccion(n,d)
        return r
    
    def iguala(self,b):
        if self.num == b.num and self.den == b.den:
            return True
        else:
            return False

def main():
    a = Fraccion(4,5)
    print(a)
    b = Fraccion(2,3)
    print(b)
    
    print(a.iguala(b))
    
    r = a+b
    print("---------------------------------------")
    print(f"Resultado de la operacion es = {r}")

if __name__ == "__main__":
    main()