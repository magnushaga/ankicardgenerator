from flask import jsonify, request
from app.models import db, Deck, Part, Chapter, Topic, Card
from . import api

@api.route('/api/decks', methods=['GET'])
def get_decks():
    """Get all decks with optional filters"""
    subject = request.args.get('subject')
    query = request.args.get('query')
    
    decks_query = Deck.query
    
    if subject:
        decks_query = decks_query.filter(Deck.subject == subject)
    if query:
        decks_query = decks_query.filter(Deck.title.ilike(f'%{query}%'))
    
    decks = decks_query.all()
    return jsonify([deck.to_dict() for deck in decks])

@api.route('/api/decks/<deck_id>', methods=['GET'])
def get_deck_details(deck_id):
    """Get detailed information about a deck"""
    deck = Deck.query.get_or_404(deck_id)
    
    # Get structure
    parts = Part.query.filter_by(deck_id=deck_id).order_by(Part.order_index).all()
    structure = {
        'parts': [{
            'id': str(part.id),
            'title': part.title,
            'chapters': [{
                'id': str(chapter.id),
                'title': chapter.title,
                'topics': [{
                    'id': str(topic.id),
                    'title': topic.title,
                    'cardCount': len(topic.cards)
                } for topic in chapter.topics]
            } for chapter in part.chapters]
        } for part in parts]
    }
    
    return jsonify({
        **deck.to_dict(),
        'structure': structure
    }) 