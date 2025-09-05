
class damage:
    def __init__(self , name , damage , hp):
        self.name = name
        self.damage = damage
        self.hp = hp
    
    def damage_calculation(self):
        self.hp -= self.damage
        if self.hp <0:
            self.hp==0
        print(f"{self.name}は{self.damage}のダメージを受けた。残りHPは{self.hp}です。")
        return self.hp
    
    def guts(self):
        hp = self.damage_calculation()
        if hp <=0:
            print(f"{self.name}は倒れた。")
        else:
            print(f"{self.name}はまだ倒れない。")

damage1 = damage("中山",20,30)
damage1.guts()
