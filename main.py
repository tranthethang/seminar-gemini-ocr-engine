from app.config import Config
from app.logging_config import setup_logging
from app.runner import Runner

def main():
    # Setup logging
    setup_logging()
    
    # Validate config
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    # Run application
    runner = Runner()
    runner.run()

if __name__ == "__main__":
    main()
