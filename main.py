from flask import jsonify
from api import create_app
from core.config import get_config
import click
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y/%I:%M:%S%p',
                    level=logging.INFO)

app = create_app()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint

    Returns:
        response: JSON response
    """
    return jsonify({'status': 'ok'})

@click.command()
@click.option('--port', default=None, help='Port to override')
def main(port: str = "", server_type: str = "standard"):
    """Main function to run the server

    Args:
        port (str, optional): _description_. Defaults to "".
        server_type (str, optional): _description_. Defaults to "".
    """
    app_config = get_config()
    app.run(debug=True, port=port or app_config.PORT )

if __name__ == '__main__':
    main()
