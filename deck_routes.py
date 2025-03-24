from flask import Blueprint, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from api import generate_cards, analyze_textbook  # Changed from generate_deck to generate_cards

deck_routes = Blueprint('deck_routes', __name__)

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='anki_test_db',
            user='postgres',
            password='admin',
            port=5432
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

@deck_routes.route('/api/decks', methods=['POST'])
def create_deck():
    data = request.json
    textbook_name = data.get('textbook_name')
    parts = data.get('parts')
    chapters = data.get('chapters')
    
    if not textbook_name:
        return jsonify({"error": "textbook_name is required"}), 400
    
    try:
        # Get subject from analyze_textbook function
        analysis_data = {"textbook_name": textbook_name}
        analysis_response = analyze_textbook()  # This will use request.get_json() internally
        if isinstance(analysis_response, tuple):
            # If it's an error response
            return analysis_response
        
        subject = analysis_response.get('primary_subject', 'general')
        
        # Generate cards using the existing function
        cards = generate_cards(textbook_name)  # Modify this according to your existing function
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            # Insert deck
            cur.execute("""
                INSERT INTO decks (textbook_name, subject, parts, chapters)
                VALUES (%s, %s, %s, %s)
                RETURNING deck_id
            """, (textbook_name, subject, parts, chapters))
            
            deck_id = cur.fetchone()[0]
            
            # Insert cards
            for card in cards:
                cur.execute("""
                    INSERT INTO cards (deck_id, front_content, back_content)
                    VALUES (%s, %s, %s)
                """, (deck_id, card['front'], card['back']))
            
            conn.commit()
            return jsonify({"message": "Deck created successfully", "deck_id": deck_id}), 201
        
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@deck_routes.route('/api/decks', methods=['GET'])
def search_decks():
    subject = request.args.get('subject')
    textbook_name = request.args.get('textbook_name')
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = "SELECT * FROM decks WHERE 1=1"
        params = []
        
        if subject:
            query += " AND subject ILIKE %s"
            params.append(f"%{subject}%")
        
        if textbook_name:
            query += " AND textbook_name ILIKE %s"
            params.append(f"%{textbook_name}%")
        
        cur.execute(query, params)
        decks = cur.fetchall()
        return jsonify(decks)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@deck_routes.route('/api/decks/<int:deck_id>', methods=['GET'])
def get_deck(deck_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get deck information
        cur.execute("SELECT * FROM decks WHERE deck_id = %s", (deck_id,))
        deck = cur.fetchone()
        
        if not deck:
            return jsonify({"error": "Deck not found"}), 404
        
        # Get cards for the deck
        cur.execute("SELECT * FROM cards WHERE deck_id = %s", (deck_id,))
        cards = cur.fetchall()
        
        deck['cards'] = cards
        return jsonify(deck)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Your route that uses the connection
@deck_routes.route('/some-endpoint', methods=['GET'])
def some_endpoint():
    conn = None
    try:
        conn = get_db_connection()
        # Your code here
        return jsonify({'message': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@deck_routes.route('/decks', methods=['GET'])
def get_decks():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM decks')
        decks = cur.fetchall()
        cur.close()
        return jsonify(decks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@deck_routes.route('/deck/<deck_id>', methods=['GET'])
def get_deck(deck_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM decks WHERE id = %s', (deck_id,))
        deck = cur.fetchone()
        cur.close()
        if deck is None:
            return jsonify({'error': 'Deck not found'}), 404
        return jsonify(deck)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()