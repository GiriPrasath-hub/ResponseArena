class CasualConversationGrader:
    def grade(self, env, *args, **kwargs) -> float:
        return 0.5


class EmotionalSupportGrader:
    def grade(self, env, *args, **kwargs) -> float:
        return 0.5


class ProfessionalReplyGrader:
    def grade(self, env, *args, **kwargs) -> float:
        return 0.5


class ProblemSolvingGrader:
    def grade(self, env, *args, **kwargs) -> float:
        return 0.5