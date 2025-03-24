from datetime import datetime, timedelta

class SuperMemo2:
    """
    Implements the SuperMemo2 spaced repetition algorithm with additional tracking
    for user-specific card states.
    """
    
    @staticmethod
    def calculate_values(quality: int, prev_easiness: float, prev_interval: int, prev_repetitions: int) -> tuple:
        """
        Calculate new SuperMemo2 values based on review quality.
        
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

    @staticmethod
    def get_next_review_date(interval: int) -> datetime:
        """Calculate the next review date based on the interval."""
        return datetime.utcnow() + timedelta(days=interval)

    @classmethod
    def update_user_card_state(cls, user_card_state, quality: int, time_taken: int = None) -> tuple:
        """
        Update a user's card state using SuperMemo2 algorithm.
        
        Args:
            user_card_state: UserCardState model instance
            quality: Integer rating from 0 to 5
            time_taken: Time taken to answer in milliseconds (optional)
        
        Returns:
            tuple: (prev_values, new_values) containing the state changes
        """
        prev_values = {
            'easiness': user_card_state.easiness,
            'interval': user_card_state.interval,
            'repetitions': user_card_state.repetitions,
            'status': user_card_state.status
        }
        
        new_easiness, new_interval, new_repetitions = cls.calculate_values(
            quality,
            user_card_state.easiness,
            user_card_state.interval,
            user_card_state.repetitions
        )
        
        # Update learning status based on performance
        if quality < 3:
            new_status = 'learning'
        elif new_repetitions >= 3 and quality >= 4:
            new_status = 'mastered'
        else:
            new_status = 'reviewing'
        
        # Update card state
        user_card_state.easiness = new_easiness
        user_card_state.interval = new_interval
        user_card_state.repetitions = new_repetitions
        user_card_state.next_review = cls.get_next_review_date(new_interval)
        user_card_state.status = new_status
        user_card_state.last_studied = datetime.utcnow()
        
        # Update performance metrics
        user_card_state.total_reviews += 1
        if quality >= 3:
            user_card_state.correct_reviews += 1
        
        if time_taken:
            # Update average response time
            if user_card_state.average_time is None:
                user_card_state.average_time = time_taken
            else:
                user_card_state.average_time = (
                    (user_card_state.average_time * (user_card_state.total_reviews - 1) + time_taken)
                    / user_card_state.total_reviews
                )
        
        new_values = {
            'easiness': new_easiness,
            'interval': new_interval,
            'repetitions': new_repetitions,
            'status': new_status,
            'next_review': user_card_state.next_review.isoformat()
        }
        
        return prev_values, new_values 