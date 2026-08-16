from app.config import Settings, get_settings


def test_default_settings_values():
    s = Settings()
    assert s.start_node == 20
    assert s.goal_node == 17
    assert s.baseline_speed == 100.0
    assert s.constraint_fraction == 0.60
    assert s.constraint_speed == 40.0
    assert s.constraint_seed == 42
    assert s.replan_fraction == 0.20
    assert s.fragility_levels == [2, 5, 8]


def test_network_data_path_points_to_real_file():
    assert Settings().network_data_path.exists()


def test_get_settings_is_cached():
    assert get_settings() is get_settings()


def test_env_prefix_override(monkeypatch):
    monkeypatch.setenv("IDRS_START_NODE", "5")
    assert Settings().start_node == 5
