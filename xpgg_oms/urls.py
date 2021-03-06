from django.urls import path, re_path, include
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from xpgg_oms.views import user, saltstack, release, menus, periodic_task
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
schema_view = get_schema_view(title='XPGG系统 API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])


router = DefaultRouter()
# 通过router注册方式配置路由，快准狠
router.register(r'userinfo', user.MyUserViewSet, base_name='userinfo')
router.register(r'saltstack/salt-key', saltstack.SaltKeyViewSet, base_name='salt-key')
router.register(r'saltstack/salt-key-opt/accept', saltstack.SaltKeyAcceptViewSet, base_name='salt-key-accept')
router.register(r'saltstack/salt-key-opt/delete', saltstack.SaltKeyDeleteViewSet, base_name='salt-key-delete')
router.register(r'saltstack/salt-key-opt/reject', saltstack.SaltKeyRejectViewSet, base_name='salt-key-reject')
router.register(r'saltstack/salt-key-opt/del-denied', saltstack.SaltKeyDeleteDeniedViewSet, base_name='salt-key-del-denied')
router.register(r'saltstack/salt-minion', saltstack.SaltMinionViewSet, base_name='salt-minion')
router.register(r'saltstack/salt-minion-opt/status-update', saltstack.SaltMinionStateUpdateViewSet, base_name='salt-minion-status-upate')
router.register(r'saltstack/salt-minion-opt/update', saltstack.SaltMinionUpdateViewSet, base_name='salt-minion-update')
router.register(r'saltstack/salt-cmd', saltstack.SaltCmdViewSet, base_name='salt-cmd')
router.register(r'saltstack/salt-cmd-opt/delete', saltstack.SaltCmdDeleteViewSet, base_name='salt-cmd-delete')
router.register(r'saltstack/salt-cmd-opt/get-module', saltstack.SaltCmdModuleListViewSet, base_name='salt-cmd-get-module')
router.register(r'saltstack/salt-cmd-opt/get-cmd', saltstack.SaltCmdCmdleListViewSet, base_name='salt-cmd-get-cmd')
router.register(r'saltstack/salt-exe', saltstack.SaltExeViewSet, base_name='salt-exe')
router.register(r'saltstack/salt-tool/job-search/status', saltstack.SaltToolJobStatusViewSet, base_name='salt-tool-job-search-status')
router.register(r'saltstack/salt-tool/job-search/result', saltstack.SaltToolJobResultViewSet, base_name='salt-tool-job-search-result')
router.register(r'saltstack/file-tree', saltstack.FileTreeModelViewSet, base_name='salt-file-tree')
router.register(r'saltstack/file-manage', saltstack.FileManageModelViewSet, base_name='salt-file-manage')
router.register(r'release/release-base', release.ReleaseModelViewSet, base_name='release-base')
router.register(r'release/release-opt', release.ReleaseOperationViewSet, base_name='release-opt')
router.register(r'release/release-del', release.ReleaseDeleteViewSet, base_name='release-del')
router.register(r'release/release-log', release.ReleaseLogViewSet, base_name='release-log')
router.register(r'release-group', release.RealseaGroupViewSet, base_name='release-group')
router.register(r'release-member', release.ReleaseGroupMemberModelViewSet, base_name='release-member')
router.register(r'release-auth', release.RealseaAuthViewSet, base_name='release-auth')
router.register(r'routes', menus.RoutesModelViewSet, base_name='routes')
router.register(r'roles', menus.RolesModelViewSet, base_name='roles')
router.register(r'users', menus.UserListModelViewSet, base_name='users')
router.register(r'periodic_task/clocked-schedule', periodic_task.ClockedScheduleModelViewSet, base_name='clocked-schedule')
router.register(r'periodic_task/clocked-list', periodic_task.ClockedListModelViewSet, base_name='clocked-list')
router.register(r'periodic_task/crontab-schedule', periodic_task.CrontabScheduleModelViewSet, base_name='crontab-schedule')
router.register(r'periodic_task/crontab-list', periodic_task.CrontabListModelViewSet, base_name='crontab-list')
router.register(r'periodic_task/interval-schedule', periodic_task.IntervalScheduleModelViewSet, base_name='interval-schedule')
router.register(r'periodic_task/interval-list', periodic_task.IntervalListModelViewSet, base_name='interval-list')
router.register(r'periodic_task/periodic-task', periodic_task.PeriodicTaskModelViewSet, base_name='periodic-task')
router.register(r'periodic_task/run-task', periodic_task.RunTaskModelViewSet, base_name='run-task')
router.register(r'periodic_task/task-log', periodic_task.TaskResultScheduleModelViewSet, base_name='task-log')


urlpatterns = [
    url(r'^docs/', schema_view, name="docs"),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^login/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^api/token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    # 把router注册的路由添加到django的url中
    url(r'', include(router.urls)),
]
