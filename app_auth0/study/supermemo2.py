from datetime import datetime, timedelta
import math

class SuperMemo2:
    def __init__(self, easiness=2.5, interval=1, repetitions=0):
        self.easiness = easiness
        self.interval = interval
        self.repetitions = repetitions
        self.next_review = datetime.utcnow()

    def calculate_next_review(self, quality):
        """
        Calculate the next review interval using the SuperMemo 2 algorithm
        quality: 0-5 rating of how well the card was remembered
        """
        if quality < 3:  # If the card was not remembered well
            self.repetitions = 0
            self.interval = 1
        else:
            self.easiness = max(1.3, self.easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
            
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = math.ceil(self.interval * self.easiness)
            
            self.repetitions += 1

        self.next_review = datetime.utcnow() + timedelta(days=self.interval)
        return self.next_review

    def to_dict(self):
        return {
            'easiness': self.easiness,
            'interval': self.interval,
            'repetitions': self.repetitions,
            'next_review': self.next_review.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            easiness=data.get('easiness', 2.5),
            interval=data.get('interval', 1),
            repetitions=data.get('repetitions', 0)
        )
        if 'next_review' in data:
            instance.next_review = datetime.fromisoformat(data['next_review'])
        return instance 