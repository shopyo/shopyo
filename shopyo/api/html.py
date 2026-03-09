from markupsafe import escape

"""
Used on flash
flash(notify_success('mail sent!'))
"""


def notify(message, alert_type="primary"):
    """
    Used with flash
        flash(notify('blabla'))

    Parameters
    ----------
    message: str
        message to be displayed

    alert_type: str
        bootstrap class

    Returns
    -------
    None
    """

    # Map bootstrap-style types to our tailwind colors
    colors = {
        "success": "emerald",
        "danger": "red",
        "warning": "amber",
        "info": "blue",
        "primary": "primary",
    }
    color = colors.get(alert_type, "primary")

    icon = "fa-info-circle"
    if alert_type == "success":
        icon = "fa-check-circle"
    elif alert_type == "danger":
        icon = "fa-exclamation-circle"
    elif alert_type == "warning":
        icon = "fa-exclamation-triangle"

    alert = f"""
    <div x-data="{{ show: true }}"
         x-show="show"
         x-init="setTimeout(() => show = false, 5000)"
         x-transition:leave="transition ease-in duration-300"
         x-transition:leave-start="opacity-100 scale-100"
         x-transition:leave-end="opacity-0 scale-95"
         class="flex items-center p-4 mb-4 rounded-2xl border bg-white dark:bg-slate-900 shadow-xl shadow-slate-200/50 dark:shadow-none border-slate-100 dark:border-slate-800 group"
         role="alert">
      <div class="flex-shrink-0 w-8 h-8 rounded-lg bg-{color if color != 'primary' else 'indigo'}-50 dark:bg-{color if color != 'primary' else 'indigo'}-900/20 flex items-center justify-center text-{color if color != 'primary' else 'indigo'}-500">
        <i class="fas {icon} text-sm"></i>
      </div>
      <div class="ml-3 text-[10px] font-black uppercase tracking-[0.15em] text-slate-600 dark:text-slate-300">
        {escape(message)}
      </div>
      <button @click="show = false" type="button" class="ml-auto w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-600 dark:hover:text-white transition-all">
        <i class="fas fa-times text-xs"></i>
      </button>
    </div>
    """
    return alert


def notify_success(message):
    return notify(message, alert_type="success")


def notify_danger(message):
    return notify(message, alert_type="danger")


def notify_warning(message):
    return notify(message, alert_type="warning")


def notify_info(message):
    return notify(message, alert_type="info")
