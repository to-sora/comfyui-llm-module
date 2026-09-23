def check_interrupt():
    from comfy.model_management import throw_exception_if_processing_interrupted
    throw_exception_if_processing_interrupted()


def interrupt_criterion():
    from transformers import StoppingCriteria, StoppingCriteriaList

    class Interrupt(StoppingCriteria):
        def __call__(self, input_ids, scores, **kwargs):
            check_interrupt()
            return False

    return StoppingCriteriaList([Interrupt()])
