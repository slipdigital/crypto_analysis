from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.index, name='index'),
    
    # Ticker routes
    path('ticker/<str:ticker_symbol>/', views.ticker_detail, name='ticker_detail'),
    path('ticker/<str:ticker_symbol>/chart/', views.ticker_chart, name='ticker_chart'),
    path('ticker/<str:ticker_symbol>/edit/', views.ticker_edit, name='ticker_edit'),
    path('ticker/<str:ticker_symbol>/toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # Chart routes
    path('charts/', views.charts, name='charts'),
    path('charts/compare/', views.charts_compare, name='charts_compare'),
    path('charts/top_gainers/', views.top_gainers, name='top_gainers'),
    
    # Indicator Type routes
    path('indicator-types/', views.indicator_types, name='indicator_types'),
    path('indicator-types/create/', views.indicator_type_create, name='indicator_type_create'),
    path('indicator-types/<int:type_id>/edit/', views.indicator_type_edit, name='indicator_type_edit'),
    path('indicator-types/<int:type_id>/delete/', views.indicator_type_delete, name='indicator_type_delete'),
    
    # Indicator routes
    path('indicators/', views.indicators, name='indicators'),
    path('indicators/create/', views.indicator_create, name='indicator_create'),
    path('indicators/<int:indicator_id>/edit/', views.indicator_edit, name='indicator_edit'),
    path('indicators/<int:indicator_id>/delete/', views.indicator_delete, name='indicator_delete'),
    
    # Indicator Data routes
    path('indicators/<int:indicator_id>/data/', views.indicator_data_list, name='indicator_data_list'),
    path('indicators/<int:indicator_id>/data/add/', views.indicator_data_add, name='indicator_data_add'),
    path('indicators/<int:indicator_id>/data/<int:data_id>/edit/', views.indicator_data_edit, name='indicator_data_edit'),
    path('indicators/<int:indicator_id>/data/<int:data_id>/delete/', views.indicator_data_delete, name='indicator_data_delete'),
    path('indicators/<int:indicator_id>/data/range-entry/', views.indicator_data_range_entry, name='indicator_data_range_entry'),
    
    # Bulk Entry route
    path('indicators/bulk-entry/', views.indicator_bulk_entry, name='indicator_bulk_entry'),
    
    # Aggregate route
    path('indicators/aggregate/', views.indicator_aggregate, name='indicator_aggregate'),
    
    # Data Updates routes
    path('data-updates/', views.data_updates, name='data_updates'),
    path('data-updates/run/<str:update_type>/', views.run_update, name='run_update'),
    path('data-updates/progress/<str:task_id>/<str:update_name>/', views.update_progress, name='update_progress'),
    path('data-updates/status/<str:task_id>/', views.update_status, name='update_status'),
]
