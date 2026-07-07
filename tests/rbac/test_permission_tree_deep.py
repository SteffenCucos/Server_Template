from service.permission_tree import PermissionTree


def build_tree(patterns: list[str]) -> PermissionTree:
    tree = PermissionTree()
    for pattern in patterns:
        tree.add(pattern)
    return tree


def test_deep_exact_path_does_not_grant_prefixes_or_children():
    tree = build_tree([
        "tenant/acme/env/prod/service/billing/resource/invoice/action/read",
    ])

    assert tree.allows("tenant/acme/env/prod/service/billing/resource/invoice/action/read")
    assert not tree.allows("tenant/acme/env/prod/service/billing/resource/invoice/action")
    assert not tree.allows("tenant/acme/env/prod/service/billing/resource/invoice/action/read/extra")
    assert not tree.allows("tenant/acme/env/staging/service/billing/resource/invoice/action/read")


def test_overlapping_exact_and_single_segment_wildcards():
    tree = build_tree([
        "tenant/acme/env/prod/service/billing/resource/invoice/action/read",
        "tenant/acme/env/prod/service/billing/resource/*/action/list",
        "tenant/acme/env/*/service/analytics/resource/report/action/read",
    ])

    assert tree.allows("tenant/acme/env/prod/service/billing/resource/invoice/action/read")
    assert tree.allows("tenant/acme/env/prod/service/billing/resource/customer/action/list")
    assert tree.allows("tenant/acme/env/staging/service/analytics/resource/report/action/read")

    assert not tree.allows("tenant/acme/env/prod/service/billing/resource/customer/action/read")
    assert not tree.allows("tenant/acme/env/prod/service/billing/resource/customer/profile/action/list")
    assert not tree.allows("tenant/acme/env/staging/service/billing/resource/invoice/action/read")


def test_deep_wildcard_grants_whole_subtree_but_not_siblings():
    tree = build_tree([
        "tenant/acme/env/prod/service/admin/**",
        "tenant/acme/env/prod/service/billing/resource/invoice/action/read",
    ])

    assert tree.allows("tenant/acme/env/prod/service/admin")
    assert tree.allows("tenant/acme/env/prod/service/admin/users")
    assert tree.allows("tenant/acme/env/prod/service/admin/users/123/roles/write")
    assert tree.allows("tenant/acme/env/prod/service/billing/resource/invoice/action/read")

    assert not tree.allows("tenant/acme/env/prod/service/billing/resource/invoice/action/write")
    assert not tree.allows("tenant/acme/env/prod/service/administer/users")
    assert not tree.allows("tenant/acme/env/staging/service/admin/users")


def test_many_sibling_branches_do_not_bleed_into_each_other():
    tree = build_tree([
        "org/*/project/*/dataset/*/read",
        "org/*/project/*/dataset/*/export/csv",
        "org/acme/project/payroll/dataset/salaries/write",
        "org/acme/project/security/**",
        "org/umbrella/project/research/dataset/virus/read",
    ])

    assert tree.allows("org/acme/project/payroll/dataset/salaries/read")
    assert tree.allows("org/acme/project/payroll/dataset/salaries/write")
    assert tree.allows("org/acme/project/payroll/dataset/salaries/export/csv")
    assert tree.allows("org/acme/project/security/incidents/2026/read")
    assert tree.allows("org/umbrella/project/research/dataset/virus/read")

    assert not tree.allows("org/acme/project/payroll/dataset/salaries/export/json")
    assert not tree.allows("org/acme/project/payroll/dataset/salaries/delete")
    assert not tree.allows("org/umbrella/project/research/dataset/virus/write")
    assert not tree.allows("org/umbrella/project/security/incidents/2026/read")


def test_wildcard_path_depth_is_strict():
    tree = build_tree([
        "read/users/*",
        "read/teams/*/members/*",
    ])

    assert tree.allows("read/users/123")
    assert tree.allows("read/teams/eng/members/456")

    assert not tree.allows("read/users/123/profile")
    assert not tree.allows("read/users")
    assert not tree.allows("read/teams/eng/members")
    assert not tree.allows("read/teams/eng/members/456/profile")


def test_deep_wildcard_can_coexist_with_more_specific_sibling_rules():
    tree = build_tree([
        "system/audit/**",
        "system/config/read",
        "system/config/secrets/*/read",
    ])

    assert tree.allows("system/audit")
    assert tree.allows("system/audit/events/2026/07/06")
    assert tree.allows("system/config/read")
    assert tree.allows("system/config/secrets/database/read")

    assert not tree.allows("system/config/write")
    assert not tree.allows("system/config/secrets/database/write")
    assert not tree.allows("system/config/secrets/database/password/read")


def test_order_of_inserted_patterns_does_not_change_results():
    patterns = [
        "a/b/c/d/e/f/g/h/i/j/read",
        "a/b/*/d/*/f/*/h/*/j/list",
        "a/b/c/d/e/f/g/**",
        "x/**",
        "x/y/z/exact",
    ]

    forward = build_tree(patterns)
    reverse = build_tree(list(reversed(patterns)))

    allowed = [
        "a/b/c/d/e/f/g/h/i/j/read",
        "a/b/other/d/other/f/other/h/other/j/list",
        "a/b/c/d/e/f/g/h/i/j/delete",
        "x",
        "x/y/z/anything",
    ]
    denied = [
        "a/b/c/d/e/f",
        "a/b/other/d/other/f/other/h/other/j/list/extra",
        "a/b/other/d/other/f/other/h/other/j/read",
        "y/x/z/anything",
    ]

    for path in allowed:
        assert forward.allows(path)
        assert reverse.allows(path)

    for path in denied:
        assert not forward.allows(path)
        assert not reverse.allows(path)
