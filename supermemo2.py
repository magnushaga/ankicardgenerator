from datetime import datetime, timedelta

def calculate_sm2_values(quality: int, prev_easiness: float, prev_interval: int, prev_repetitions: int) -> tuple:
    """
    Implements the SuperMemo2 algorithm for spaced repetition.
    
    Args:
        quality: Integer rating from 0 to 5 of how well the card was remembered
        prev_easiness: Previous easiness factor
        prev_interval: Previous interval in days
        prev_repetitions: Number of times the card has been successfully reviewed
    
    Returns:
        tuple: (new_easiness, new_interval, new_repetitions)
    """
    if quality < 3:
        # If quality is less than 3, reset repetitions and interval
        new_repetitions = 0
        new_interval = 1
    else:
        new_repetitions = prev_repetitions + 1
        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = round(prev_interval * prev_easiness)
    
    # Calculate new easiness factor
    new_easiness = prev_easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    # Ensure easiness doesn't go below 1.3
    new_easiness = max(1.3, new_easiness)
    
    return new_easiness, new_interval, new_repetitions

def get_next_review_date(interval: int) -> datetime:
    """Calculate the next review date based on the interval."""
    return datetime.utcnow() + timedelta(days=interval)

def update_card_review(card, quality: int) -> tuple:
    """
    Update a card's SuperMemo2 values based on the review quality.
    
    Args:
        card: Card model instance
        quality: Integer rating from 0 to 5
    
    Returns:
        tuple: (prev_values, new_values) where each value is a dict containing easiness, interval, and repetitions
    """
    prev_values = {
        'easiness': card.easiness,
        'interval': card.interval,
        'repetitions': card.repetitions
    }
    
    new_easiness, new_interval, new_repetitions = calculate_sm2_values(
        quality,
        card.easiness,
        card.interval,
        card.repetitions
    )
    
    new_values = {
        'easiness': new_easiness,
        'interval': new_interval,
        'repetitions': new_repetitions
    }
    
    # Update card
    card.easiness = new_easiness
    card.interval = new_interval
    card.repetitions = new_repetitions
    card.next_review = get_next_review_date(new_interval)
    
    return prev_values, new_values