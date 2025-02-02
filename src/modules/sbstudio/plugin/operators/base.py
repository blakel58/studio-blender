from bpy.types import Collection, Operator

from sbstudio.plugin.errors import StoryboardValidationError
from sbstudio.plugin.selection import select_only


class FormationOperator(Operator):
    """Operator mixin that allows an operator to be executed if we have a
    selected formation in the current scene.
    """

    @classmethod
    def poll(cls, context):
        return (
            context.scene.skybrush
            and context.scene.skybrush.formations
            and (
                getattr(cls, "works_with_no_selected_formation", False)
                or context.scene.skybrush.formations.selected
            )
        )

    def execute(self, context):
        return self.execute_on_formation(self.get_formation(context), context)

    def get_formation(self, context) -> Collection:
        return getattr(context.scene.skybrush.formations, "selected", None)

    @staticmethod
    def select_formation(formation, context) -> None:
        """Selects the given formation, both in the scene and in the formations
        panel.
        """
        select_only(formation)
        if context.scene.skybrush.formations:
            context.scene.skybrush.formations.selected = formation


class LightEffectOperator(Operator):
    """Operator mixin that allows an operator to be executed if we have a
    light effects object in the current scene.
    """

    @classmethod
    def poll(cls, context):
        return context.scene.skybrush and context.scene.skybrush.light_effects

    def execute(self, context):
        light_effects = context.scene.skybrush.light_effects
        return self.execute_on_light_effect_collection(light_effects, context)


class StoryboardOperator(Operator):
    """Operator mixin that allows an operator to be executed if we have a
    storyboard in the current scene.
    """

    @classmethod
    def poll(cls, context):
        return context.scene.skybrush and context.scene.skybrush.storyboard

    def execute(self, context):
        storyboard = context.scene.skybrush.storyboard

        validate = getattr(self.__class__, "only_with_valid_storyboard", False)

        if validate:
            try:
                entries = storyboard.validate_and_sort_entries()
            except StoryboardValidationError as ex:
                self.report({"ERROR_INVALID_INPUT"}, str(ex))
                return {"CANCELLED"}

            return self.execute_on_storyboard(storyboard, entries, context)
        else:
            return self.execute_on_storyboard(storyboard, context)


class StoryboardEntryOperator(Operator):
    """Operator mixin that allows an operator to be executed if we have a
    selected storyboard entry in the current scene.
    """

    @classmethod
    def poll(cls, context):
        return (
            context.scene.skybrush
            and context.scene.skybrush.storyboard
            and context.scene.skybrush.storyboard.active_entry
        )

    def execute(self, context):
        entry = context.scene.skybrush.storyboard.active_entry
        return self.execute_on_storyboard_entry(entry, context)
