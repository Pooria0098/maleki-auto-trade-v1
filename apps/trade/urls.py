from django.urls import path
from apps.trade import views

app_name = 'trades'
urlpatterns = [
  path('ultra-dca/list/', views.UltraDCAListView.as_view(), name='ultra_dca_list'),
  path('ultra-dca/list/<str:api>/', views.UltraDCAListView.as_view(), name='ultra_dca_list_with_api'),
  path('ultra-dca/create/smart/', views.UltraDCASmartCreateView.as_view(), name='ultra_dca_smart_create'),
  path('ultra-dca/create/advanced/', views.UltraDCAAdvancedCreateView.as_view(), name='ultra_dca_advanced_create'),
  # path('ultra-dca/<int:pk>/'),
  path('ultra-dca/<int:pk>/update/', views.UltraDCAUpdateView.as_view(), name='ultra_dca_update'),
  # path('ultra-dca/<int:pk>/toggle/activation/'),
  # path('ultra-dca/<int:pk>/toggle/buy/'),
  # path('ultra-dca/<int:pk>/toggle/sell/'),
  # path('ultra-dca/<int:pk>/stop/all/'),
  path('ultra-dca/<int:system_id>/engines/', views.UltraDCAEnginesView.as_view(), name='ultra_dca_engines'),
  path('ultra-dca/<int:engine_id>/orders/', views.UltraDCAOrdersView.as_view(), name='ultra_dca_orders'),
  path('ultra-dca/<int:order_id>/exchange-orders/', views.UltraDCAExchangeOrdersView.as_view(),
       name='ultra_dca_exchange_orders'),

  path('ultra-grid/list/', views.UltraGridListView.as_view(), name='ultra_grid_list'),
  path('ultra-grid/list/<str:api>/', views.UltraGridListView.as_view(), name='ultra_grid_list_with_api'),
  path('ultra-grid/create/smart/', views.UltraGridSmartCreateView.as_view(), name='ultra_grid_smart_create'),
  path('ultra-grid/create/advanced/', views.UltraGridAdvancedCreateView.as_view(), name='ultra_grid_advanced_create'),
  # path('ultra-grid/<int:pk>/'),
  path('ultra-grid/<int:pk>/update/', views.UltraGridUpdateView.as_view(), name='ultra_grid_update'),
  # path('ultra-grid/<int:pk>/toggle/activation/'),
  # path('ultra-grid/<int:pk>/toggle/buy/'),
  # path('ultra-grid/<int:pk>/toggle/sell/'),
  # path('ultra-grid/<int:pk>/stop/all/'),
  path('ultra-grid/<int:system_id>/parts/', views.UltraGridPartsView.as_view(), name='ultra_grid_parts'),
  path('ultra-grid/<int:part_id>/orders/', views.UltraGridOrdersView.as_view(), name='ultra_grid_orders'),
  path('ultra-grid/<int:order_id>/exchange-orders/', views.UltraGridExchangeOrdersView.as_view(),
       name='ultra_grid_exchange_orders'),
]
