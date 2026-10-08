class Scores:
    def __init__(self, engine, tokenizer):
        self.rows = engine.diagnostics['generation_scores'] = []
        self.tokenizer = tokenizer

    def __call__(self, input_ids, scores):
        if len(self.rows) < 6:
            values, ids = scores[0].topk(5)
            self.rows.append([{'token':self.tokenizer.decode([ident]),'logit':value}
                              for ident,value in zip(ids.tolist(),values.tolist())])
        return scores
