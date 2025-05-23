from app.listeners import listeners
from app.routes import blueprint_group
from torpedo import Torpedo

torpedo = Torpedo(blueprint_group, listeners)
app = torpedo.create_app()
if __name__ == "__main__":
    torpedo.run()

