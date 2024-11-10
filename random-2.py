import json
import random

class Character:
    def __init__(self, name, character_class, hp, attack, defense):
        self.name = name
        self.character_class = character_class
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.inventory = []

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def attack_target(self, target):
        damage = max(1, self.attack - target.defense)
        target.take_damage(damage)
        return damage

    def add_to_inventory(self, item):
        self.inventory.append(item)

    def show_inventory(self):
        if self.inventory:
            print(f"{self.name}'s Inventory: " + ", ".join(self.inventory))
        else:
            print(f"{self.name}'s inventory is empty.")

class Enemy(Character):
    def __init__(self, name, hp, attack, defense):
        super().__init__(name, None, hp, attack, defense)

class Game:
    def __init__(self):
        self.player = None
        self.enemies = []
        self.load_enemies()
        self.locations = {
            "Village": "A small, peaceful village with friendly people.",
            "Forest": "A dark, dense forest filled with dangerous creatures.",
            "Cave": "A deep cave that holds many secrets and treasures.",
            "Castle": "A grand castle with a mighty king."
        }
        self.current_location = "Village"
        self.quests = [
            {"name": "Find the Lost Sword", "completed": False},
            {"name": "Defeat the Dragon", "completed": False}
        ]

    def load_enemies(self):
        enemy_data = [
            {"name": "Goblin", "hp": 30, "attack": 5, "defense": 2},
            {"name": "Orc", "hp": 50, "attack": 7, "defense": 3},
            {"name": "Dragon", "hp": 200, "attack": 20, "defense": 10}
        ]
        for data in enemy_data:
            self.enemies.append(Enemy(data["name"], data["hp"], data["attack"], data["defense"]))

    def create_player(self):
        name = input("Enter your character's name: ")
        character_class = input("Choose your class (Warrior, Mage, Archer): ")
        if character_class == "Warrior":
            self.player = Character(name, character_class, 120, 15, 10)
        elif character_class == "Mage":
            self.player = Character(name, character_class, 80, 20, 5)
        elif character_class == "Archer":
            self.player = Character(name, character_class, 100, 18, 7)
        else:
            print("Invalid class. Defaulting to Warrior.")
            self.player = Character(name, "Warrior", 120, 15, 10)

    def save_game(self):
        save_data = {
            "player": {
                "name": self.player.name,
                "class": self.player.character_class,
                "hp": self.player.hp,
                "attack": self.player.attack,
                "defense": self.player.defense,
                "inventory": self.player.inventory
            },
            "enemies": [
                {"name": enemy.name, "hp": enemy.hp, "attack": enemy.attack, "defense": enemy.defense}
                for enemy in self.enemies
            ],
            "location": self.current_location,
            "quests": self.quests
        }
        with open('savegame.json', 'w') as file:
            json.dump(save_data, file)
        print("Game saved!")

    def load_game(self):
        try:
            with open('savegame.json', 'r') as file:
                save_data = json.load(file)
            player_data = save_data["player"]
            self.player = Character(player_data["name"], player_data["class"], player_data["hp"], player_data["attack"], player_data["defense"])
            self.player.inventory = player_data["inventory"]

            self.enemies = []
            for enemy_data in save_data["enemies"]:
                self.enemies.append(Enemy(enemy_data["name"], enemy_data["hp"], enemy_data["attack"], enemy_data["defense"]))

            self.current_location = save_data["location"]
            self.quests = save_data["quests"]
            print("Game loaded!")
        except FileNotFoundError:
            print("No save file found.")

    def show_status(self):
        print(f"Player: {self.player.name} - Class: {self.player.character_class} - HP: {self.player.hp}")
        self.player.show_inventory()
        print(f"Current Location: {self.current_location}")
        print("Quests:")
        for quest in self.quests:
            status = "Completed" if quest["completed"] else "Incomplete"
            print(f" - {quest['name']}: {status}")

    def player_turn(self, enemy):
        print(f"\nYour turn! Choose an action:")
        print("1. Attack")
        print("2. Use Item")
        choice = input("Enter the number of your choice: ")
        if choice == '1':
            damage = self.player.attack_target(enemy)
            print(f"You attacked {enemy.name} for {damage} damage.")
        elif choice == '2':
            self.player.show_inventory()
            item = input("Enter the name of the item to use: ")
            if item in self.player.inventory:
                self.player.inventory.remove(item)
                print(f"You used the {item}.")
            else:
                print("You don't have that item.")

    def enemy_turn(self, enemy):
        if enemy.is_alive():
            damage = enemy.attack_target(self.player)
            print(f"{enemy.name} attacked you for {damage} damage.")

    def combat(self, enemy):
        while self.player.is_alive() and enemy.is_alive():
            self.player_turn(enemy)
            if enemy.is_alive():
                self.enemy_turn(enemy)
            self.show_status()
        if self.player.is_alive():
            print(f"You have defeated the {enemy.name}!")
            self.player.add_to_inventory(f"{enemy.name}'s loot")
            for quest in self.quests:
                if quest["name"] == "Defeat the Dragon" and enemy.name == "Dragon":
                    quest["completed"] = True
        else:
            print("You have been defeated!")

    def explore(self):
        print("\nChoose a location to explore:")
        for i, location in enumerate(self.locations.keys(), 1):
            print(f"{i}. {location}")
        choice = int(input("Enter the number of your choice: "))
        new_location = list(self.locations.keys())[choice - 1]
        self.current_location = new_location
        print(f"You arrived at the {new_location}. {self.locations[new_location]}")

        if new_location == "Forest":
            if not any(enemy.name == "Goblin" for enemy in self.enemies):
                print("You encounter a Goblin!")
                enemy = Enemy("Goblin", 30, 5, 2)
                self.combat(enemy)
        elif new_location == "Cave":
            if not any(enemy.name == "Orc" for enemy in self.enemies):
                print("You encounter an Orc!")
                enemy = Enemy("Orc", 50, 7, 3)
                self.combat(enemy)
        elif new_location == "Castle":
            if not any(enemy.name == "Dragon" for enemy in self.enemies):
                print("You encounter a Dragon!")
                enemy = Enemy("Dragon", 200, 20, 10)
                self.combat(enemy)

    def start_game(self):
        print("Welcome to the Text Adventure Game!")
        print("1. New Game")
        print("2. Load Game")
        choice = input("Enter the number of your choice: ")
        if choice == '1':
            self.create_player()
        elif choice == '2':
            self.load_game()
        else:
            print("Invalid choice. Starting a new game.")
            self.create_player()

        while self.player.is_alive():
            print("\nWhat would you like to do?")
            print("1. Explore")
            print("2. View status")
            print("3. Save game")
            print("4. Quit game")
            choice = input("Enter the number of your choice: ")
            if choice == '1':
                self.explore()
            elif choice == '2':
                self.show_status()
            elif choice == '3':
                self.save_game()
            elif choice == '4':
                print("Thank you for playing!")
                break
            else:
                print("Invalid choice. Try again.")

if __name__ == "__main__":
    game = Game()
    game.start_game()
