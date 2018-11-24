from abc import ABCMeta, abstractproperty

from RavensSemanticRelationship import (AddKeepDelete2x2, FindMissingShapeAndCount, FindAndMergeCommonShapesRowColumn,
                                        FindMissingCenterShapeAndApplyPattern, FindMissingCenterShapeAndMissingPattern,
                                        FindMissingFrame, FindMissingImagePattern, InvertedDiagonalUnion,
                                        ShapeFillPointsSystem3x3, ShapeScaling3x3, SidesArithmetic)


class RavensSemanticSolverFactory:
    def __init__(self):
        pass

    def create(self, problem_type):
        """
        Creates an instance of a RavensSemanticSolver for the given problem type.

        :param problem_type: The problem type, either '2x2' or '3x3'.
        :type problem_type: str
        :return: A RavensSemanticSolver.
        :rtype: RavensSemanticSolver
        """
        if problem_type == '2x2':
            return _RavensSemantic2x2Solver()
        elif problem_type == '3x3':
            return _RavensSemantic3x3Solver()
        else:
            raise ValueError('Invalid problem type: {}'.format(problem_type))


class RavensSemanticSolver:
    __metaclass__ = ABCMeta

    def run(self, problem):
        """
        Runs this solver to find an answer to the given problem.

        :param problem: The RPM problem to solve.
        :type problem: RavensVisualProblem.RavensVisualProblem
        :return: The index of the selected answer, or None if no answer could be chosen.
        :rtype: int
        """
        # Since the semantic relationships are more computationally expensive, generate and test one by one
        for relationship in self._relationships:
            answers = []

            for axis in self._axes:
                if not relationship.is_valid(axis):
                    continue

                expected = relationship.generate(problem.matrix, axis)
                answer = relationship.test(expected, problem.matrix, problem.answers, axis)
                answers.append(answer)

            # If the answers match from the semantic relationships generated by the axes,
            # then take this answer as the desired one and stop evaluating any other relationships
            # as long as that answer is not `None`
            if len(set(answers)) == 1 and answers[0] is not None:
                return answers[0]

        return None

    @abstractproperty
    def _relationships(self):
        # The list of all available semantic relationships for this solver
        pass

    @abstractproperty
    def _axes(self):
        # The list of valid axes for this solver
        pass


class _RavensSemantic2x2Solver(RavensSemanticSolver):
    @property
    def _relationships(self):
        return [
            AddKeepDelete2x2(),
            SidesArithmetic()
        ]

    @property
    def _axes(self):
        return [0, 1]


class _RavensSemantic3x3Solver(RavensSemanticSolver):
    @property
    def _relationships(self):
        return [
            ShapeScaling3x3(),
            ShapeFillPointsSystem3x3(),
            InvertedDiagonalUnion(),
            FindMissingFrame(),
            FindAndMergeCommonShapesRowColumn(),
            FindMissingCenterShapeAndApplyPattern(),
            FindMissingCenterShapeAndMissingPattern([
                FindMissingCenterShapeAndMissingPattern.SURROUNDED_BY_SHAPES,
                FindMissingCenterShapeAndMissingPattern.INSIDE_OTHER_SHAPE,
                FindMissingCenterShapeAndMissingPattern.INSIDE_SAME_SHAPE
            ]),
            FindMissingCenterShapeAndMissingPattern([
                FindMissingCenterShapeAndMissingPattern.FILLED_SHAPE,
                FindMissingCenterShapeAndMissingPattern.EMPTY_SHAPE,
                FindMissingCenterShapeAndMissingPattern.INSIDE_SAME_SHAPE
            ]),
            FindMissingImagePattern(FindMissingImagePattern.ROTATION_AND_UNION),
            FindMissingShapeAndCount()
        ]

    @property
    def _axes(self):
        return [0, 1, 2]
