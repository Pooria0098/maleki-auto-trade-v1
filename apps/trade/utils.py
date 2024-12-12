from apps.trade.models import SystemStatus
from apps.users.models import ApiStatus


def get_user_apis(self):
  user = self.request.user
  apis = user.api_set.filter(status=ApiStatus.Active)
  api_list = [
    {"id": api.id, "name": str(api)}
    for api in apis
  ]
  return api_list


def get_user_robots_status(self, bot_type):
  user = self.request.user
  apis = user.api_set.filter(status=ApiStatus.Active)

  Total_bots = 0
  Running_bots = 0
  Stop_bots = 0
  Busy_bots = 0

  if not apis:
    return {
      'Total_bots': Total_bots,
      'Running_bots': Running_bots,
      'Stop_bots': Stop_bots,
      'Busy_bots': Busy_bots,
    }
  api_id = self.kwargs.get('api')
  if api_id:
    apis = apis.filter(id=api_id)

  if bot_type == 'DCA':
    for api in apis:
      Total_bots += api.ultradcasystem_set.all().count()
      Running_bots += api.ultradcasystem_set.filter(status=SystemStatus.Running).count()
      Stop_bots += api.ultradcasystem_set.filter(status=SystemStatus.Stop).count()
      Busy_bots += api.ultradcasystem_set.filter(status=SystemStatus.Busy).count()
  else:
    for api in apis:
      Total_bots += api.ultragridsystem_set.all().count()
      Running_bots += api.ultragridsystem_set.filter(status=SystemStatus.Running).count()
      Stop_bots += api.ultragridsystem_set.filter(status=SystemStatus.Stop).count()
      Busy_bots += api.ultragridsystem_set.filter(status=SystemStatus.Busy).count()

  return {
    'Total_bots': Total_bots,
    'Running_bots': Running_bots,
    'Stop_bots': Stop_bots,
    'Busy_bots': Busy_bots,
  }
