#!/usr/bin/env python3
import random
import re
from collections import defaultdict
from src.application.model.parser.prep_data import generate_lyrics

class MarkovModel:
    def __init__(self, order=2):
        self.order = order
        self.model = defaultdict(list)
        self.starts = []
        
    def train(self, sentences):
        for sentence in sentences:
            words = re.findall(r'\b\w+\b|[.!?,]', sentence.lower())
            if len(words) <= self.order:
                continue
            self.starts.append(tuple(words[:self.order]))
            for i in range(len(words) - self.order):
                ctx = tuple(words[i:i+self.order])
                self.model[ctx].append(words[i + self.order])
                
    def generate_with_backoff(self, models, seed_words=None, max_length=50):
        if not self.model:
            return "Model has not been trained yet."
        # choose start
        if seed_words and len(seed_words) >= self.order:
            current = tuple(seed_words[-self.order:])
            result = seed_words.copy()
        else:
            if not self.starts:
                return "Cannot generate text: no sentence starts found."
            current = random.choice(self.starts)
            result = list(current)

        # generate
        while len(result) < max_length:
            if current in self.model:
                nxt = random.choice(self.model[current])
            else:
                # back off
                found = False
                for o in range(self.order - 1, 0, -1):
                    if o in models and len(result) >= o:
                        short = tuple(result[-o:])
                        if short in models[o].model:
                            nxt = random.choice(models[o].model[short])
                            found = True
                            break
                if not found:
                    base = models.get(1)
                    if base and base.model:
                        ctx = random.choice(list(base.model.keys()))
                        nxt = random.choice(base.model[ctx])
                    else:
                        break

            result.append(nxt)
            current = tuple(result[-self.order:])
            if nxt in {'.','!','?'} and len(result) > max_length//2:
                break

        # tidy punctuation
        out = []
        for i, w in enumerate(result):
            if w in {',','.','!','?'}:
                out[-1] += w
            else:
                out.append(w)
        return ' '.join(out)
