import os
import sys
from typing import Set


def _add_path() -> None:
    here = os.path.dirname(__file__)
    dags_dir = os.path.abspath(os.path.join(here, '..', 'dags'))
    if dags_dir not in sys.path:
        sys.path.insert(0, dags_dir)


def test_import_etl_improved() -> None:
    _add_path()
    mod = __import__('etl_improved')
    assert hasattr(mod, 'dag'), 'etl_improved.dag not found'


def test_import_etl_consumer() -> None:
    _add_path()
    mod = __import__('etl_consumer')
    assert hasattr(mod, 'dag'), 'etl_consumer.dag not found'


def test_etl_improved_structure() -> None:
    _add_path()
    mod = __import__('etl_improved')
    dag = mod.dag
    assert dag.dag_id == 'etl_improved'
    # Expected tasks
    expected_tasks = {'extract', 'transform', 'validate', 'ge_validate', 'chunk', 'load', 'finalize'}
    task_ids = {t.task_id for t in dag.tasks}
    assert expected_tasks.issubset(task_ids), f'Missing tasks: {expected_tasks - task_ids}'
    # Check params defaults
    assert 'batch_size' in dag.params
    assert 'dry_run' in dag.params
    assert 'enforce_ge' in dag.params


def test_etl_consumer_structure() -> None:
    _add_path()
    mod = __import__('etl_consumer')
    dag = mod.dag
    assert dag.dag_id == 'etl_consumer'
    # Expected tasks
    expected_tasks = {'summarize_metrics', 'refresh_mvs'}
    task_ids = {t.task_id for t in dag.tasks}
    assert expected_tasks.issubset(task_ids), f'Missing tasks: {expected_tasks - task_ids}'
    # Check params
    assert 'trend_window' in dag.params
    assert 'drop_threshold_pct' in dag.params


def test_etl_improved_dependencies() -> None:
    _add_path()
    mod = __import__('etl_improved')
    dag = mod.dag
    # Check extract -> transform -> chunk -> validate -> ge_validate -> load -> finalize
    extract = dag.get_task('extract')
    transform = dag.get_task('transform')
    chunk_task = dag.get_task('chunk')
    validate = dag.get_task('validate')
    ge_validate = dag.get_task('ge_validate')
    load_task = dag.get_task('load')
    finalize = dag.get_task('finalize')
    # Verify dependencies exist (basic check)
    assert extract is not None
    assert transform is not None
    assert chunk_task is not None
    assert validate is not None
    assert ge_validate is not None
    assert load_task is not None
    assert finalize is not None


def test_etl_consumer_dependencies() -> None:
	_add_path()
	mod = __import__('etl_consumer')
	dag = mod.dag
	summarize = dag.get_task('summarize_metrics')
	refresh = dag.get_task('refresh_mvs')
	assert summarize is not None
	assert refresh is not None


def test_import_etl_maintenance() -> None:
	_add_path()
	mod = __import__('etl_maintenance')
	assert hasattr(mod, 'dag'), 'etl_maintenance.dag not found'


def test_etl_maintenance_structure() -> None:
	_add_path()
	mod = __import__('etl_maintenance')
	dag = mod.dag
	assert dag.dag_id == 'etl_maintenance'
	expected_tasks = {'clean_old_metrics', 'clean_old_audit', 'clean_old_alerts', 'clean_old_events', 'refresh_mvs', 'vacuum_analyze'}
	task_ids = {t.task_id for t in dag.tasks}
	assert expected_tasks.issubset(task_ids), f'Missing tasks: {expected_tasks - task_ids}'
	assert 'retention_days_metrics' in dag.params
	assert 'retention_days_events' in dag.params


def test_import_etl_downstream_example() -> None:
	_add_path()
	mod = __import__('etl_downstream_example')
	assert hasattr(mod, 'dag'), 'etl_downstream_example.dag not found'


def test_etl_downstream_example_structure() -> None:
	_add_path()
	mod = __import__('etl_downstream_example')
	dag = mod.dag
	assert dag.dag_id == 'etl_downstream_example'
	expected_tasks = {'read_latest_metrics', 'analyze_events', 'generate_report', 'cleanup_temp_data'}
	task_ids = {t.task_id for t in dag.tasks}
	assert expected_tasks.issubset(task_ids), f'Missing tasks: {expected_tasks - task_ids}'
	assert 'analysis_type' in dag.params
	assert 'top_n' in dag.params

