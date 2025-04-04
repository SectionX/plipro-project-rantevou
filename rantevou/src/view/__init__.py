from collections import OrderedDict

from .window import Window
from .abstract_views import AppFrame
from .overview import Overview
from .statistics import Statistics
from .customers import Customers
from .appointments import Appointments
from .alerts import Alerts

dict_: OrderedDict[str, AppFrame | Overview] = OrderedDict()

root = Window()
dict_["overview"] = Overview(root)
dict_["appointments"] = Appointments(root)
dict_["customers"] = Customers(root)
dict_["statistics"] = Statistics(root)
dict_["alerts"] = Alerts(root)

root.initialize_frames(dict_)
