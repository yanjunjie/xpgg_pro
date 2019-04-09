# 公用全局方法
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.utils import six
from rest_framework.serializers import Serializer
from rest_framework.pagination import PageNumberPagination
import logging
logger = logging.getLogger('xpgg_oms.views')


# 自定义rest framework的异常捕获返回,在settings里调用
def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['code'] = response.status_code
        # 这个可以使所有错误码改成200返回，然后在code中指定返回码
        # response.status_code = 200
        try:
            # 可能没有detail所以要用try
            response.data['message'] = response.data['detail']
            del response.data['detail']
        except Exception as e:
            pass

    return response

# 参考：
# def custom_exception_handler(exc, context):
#     # Call REST framework's default exception handler first,
#     # to get the standard error response.
#     response = exception_handler(exc, context)
#
#     # Now add the HTTP status code to the response.
#     if response is not None:
#         print(response.data)
#         response.data.clear()
#         response.data['code'] = response.status_code
#         response.data['data'] = []
#
#         if response.status_code == 404:
#             try:
#                 response.data['message'] = response.data.pop('detail')
#                 response.data['message'] = "Not found"
#             except KeyError:
#                 response.data['message'] = "Not found"
#
#         if response.status_code == 400:
#             response.data['message'] = 'Input error'
#
#         elif response.status_code == 401:
#             response.data['message'] = "Auth failed"
#
#         elif response.status_code >= 500:
#             response.data['message'] =  "Internal service errors"
#
#         elif response.status_code == 403:
#             response.data['message'] = "Access denied"
#
#         elif response.status_code == 405:
#             response.data['message'] = 'Request method error'
#     return response


# 自定义Response返回，把原来返回的data放到下一层即data.data，然后在data中添加code，message等,目前还没有用到
class MyResponse(Response):
    """
    An HttpResponse that allows its data to be rendered into
    arbitrary media types.
    """

    def __init__(self, data=None, code=None, msg=None,
                 status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.
        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super(Response, self).__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = {"code": code, "message": msg, "data": data}
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in six.iteritems(headers):
                self[name] = value


# 分页代码
class StandardPagination(PageNumberPagination):
    # 每页显示个数
    page_size = 1
    # url中默认修改每页个数的参数名
    # 比如http://127.0.0.1:8000/api/snippets/?page=1&page_size=4
    # 就是显示第一页并且显示个数是4个
    # page_size的变量名称默认如下
    page_size_query_param = 'page_size'
    # url中默认是参数名是page下面还是改成page哈
    page_query_param = "page"
    # 每页最大个数不超过100
    max_page_size = 100

    # 自定义数据,
    msg = None

    def paginate_queryset(self, queryset, request, view=None):
        """
        获取分页内容
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        # 重定义错误，默认如果页数page超过分页大小会报错，这里改成超过的话页数变成第一页
        # page_number是传递进来要展示第几页的页数
        try:
            self.page = paginator.page(page_number)
        except Exception as e:
            self.page = paginator.page(1)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        """
        设置返回内容格式
        """
        return Response({
            'results': data,
            'count': self.page.paginator.count,
            'page_size': self.page.paginator.per_page,
            'page': self.page.start_index(),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'msg': self.msg
        })


# salt执行state.sls的返回结果格式化，因为通过api返回的结果不怎么好看呵呵
def format_state(result):
    a = result['results']
    # b是返回minion列表
    b = (a['return'])
    # 用来存放所有minion格式化后的结果的
    result_data = []
    try:
        # i是return后面的列表其实就是a['return'][0]
        for i in b:
            # key是minion的ID,value是这个ID执行的所有结果又是一个字典
            for key, value in i.items():
                succeeded = 0
                failed = 0
                changed = 0
                Total_states_run = 0
                Total_run_time = 0
                minion_id = key
                run_num = len(value)  # 得到执行的state个数
                result_list = [k for k in range(run_num)] #把列表先用数字撑大，因为接收的数据随机的顺序如（3,5,6），先撑开列表到时候假设是3过来就插3的位子这样顺序就有序了
                for key1, value1 in value.items():
                    # print(value1)
                    # key1是一个个state的ID，value1是每个state的结果
                    key1 = key1.split('_|-')
                    Function = key1[0] + '_' + key1[-1]
                    ID = key1[1]
                    Name = key1[2]
                    aaa = '----------\n' + 'ID: '.rjust(14) + ID + '\n' + 'Function: '.rjust(
                        14) + Function + '\n' + 'Name: '.rjust(14) + Name + '\n' + 'Result: '.rjust(14) + str(
                        value1['result']) + '\n' + 'Comment: '.rjust(14) + value1['comment'] + '\n'
                    # start_time有的没有有的有
                    if value1.get('start_time'):
                        aaa += 'Started: '.rjust(14) + str(value1['start_time']) + '\n'
                    # duration有的没有有的有
                    if value1.get('duration'):
                        aaa += 'Duration: '.rjust(14) + str(value1['duration']) + ' ms' + '\n'
                        Total_run_time += value1['duration']
                    # changes都有，就算没值也是一个空的{}
                    if value1['changes'] == {}:
                        aaa += 'Changes: '.rjust(14)+'\n'
                    elif type(value1['changes']) == str:
                        aaa += 'ChangesIs: '.rjust(14) + '\n' + ''.rjust(14) + '----------\n'
                        aaa += ''.rjust(14) + value1['changes'] + ':\n' + ''.rjust(18) + '----------\n'
                    else:
                        aaa += 'ChangesIs: '.rjust(14) + '\n' + ''.rjust(14) + '----------\n'
                        for key in value1['changes'].keys():

                            if type(value1['changes'][key]) == dict:
                                aaa += ''.rjust(14) + key + ':\n' + ''.rjust(18) + '----------\n'
                                for ckey, cvalue in value1['changes'][key].items():
                                    aaa += ''.rjust(18) + ckey + ':\n' + ''.rjust(22) + str(cvalue).replace('\n','\n'+' '*18) + '\n'
                            else:
                                aaa += ''.rjust(14) + key + ':\n' + ''.rjust(18) + str(value1['changes'][key]).replace('\n','\n'+' '*18) + '\n'
                        changed += 1
                    if value1.get('__run_num__') is None:
                        result_list.append(aaa)
                    else:
                        result_list[value1.get('__run_num__')] = aaa
                    if value1['result']:
                        succeeded += 1
                    else:
                        failed += 1
                    Total_states_run += 1
                Total_run_time = Total_run_time / 1000
                bbb =74*'-'+ '\nSummary for %s\n-------------\nSucceeded: %d (changed=%d)\nFailed:    %2d\n-------------\nTotal states run:     %d\nTotal run time:    %.3f s\n\n' % (
                minion_id, succeeded, changed, failed, Total_states_run, Total_run_time)
                result_list.insert(0, bbb)
                result_data.extend(result_list)
        return result_data
    #如果格式化有问题，就把原来的以str来返回，然后在调用这个格式化的方法里写判断如果为str说明格式化失败，然后该怎么处理就怎么处理呵呵
    except Exception as e:
        logger.error('格式化不成功'+str(e))
        return str(a)







