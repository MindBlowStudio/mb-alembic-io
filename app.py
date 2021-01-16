import sgtk
from sgtk.platform import Application

logger = sgtk.platform.get_logger(__name__)


class StgkStarterApp(Application):

    def init_app(self):
        app_payload = self.import_module("app")
        menu_callback = lambda: app_payload.dialog.show_dialog(self)
        self.engine.register_command("MB Alembic", menu_callback)

    def destroy_app(self):
        logger.debug("Destroying MB Alembic")