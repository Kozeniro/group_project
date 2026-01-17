package auth

const (
	RoleUser    = "student"
	RoleTeacher = "teacher"
	RoleAdmin   = "admin"
)

var RolePermissions = map[string][]string{
	RoleUser: {
		"user:data:read",
		"user:roles:read",
		"user:roles:write",
		"user:block:read",
		"user:block:write",
		"course:info:write",
		"course:testList",
		"course:test:read",
		"course:test:write",
		"course:test:add",
		"course:test:del",
		"course:userList",
		"course:user:add",
		"course:user:del",
		"course:del",
		"quest:list:read",
		"quest:read",
		"quest:update",
		"quest:del",
		"answer:update",
		"answer:del",
	},
	RoleTeacher: {
		"user:data:read",
		"user:roles:read",
		"user:roles:write",
		"user:block:read",
		"user:block:write",
		"course:info:write",
		"course:testList",
		"course:test:read",
		"course:test:write",
		"course:test:add",
		"course:test:del",
		"course:userList",
		"course:user:add",
		"course:user:del",
		"course:del",
		"quest:list:read",
		"quest:read",
		"quest:update",
		"quest:del",
		"answer:update",
		"answer:del",
		"test:quest:del",
		"test:quest:add",
		"test:quest:update",
		"test:answer:read",
		"answer:read",
	},
	RoleAdmin: {
		"user:list:read",
		"user:fullName:write",
		"user:data:read",
		"user:roles:read",
		"user:roles:write",
		"user:block:read",
		"user:block:write",
		"course:info:write",
		"course:testList",
		"course:test:read",
		"course:test:write",
		"course:test:add",
		"course:test:del",
		"course:userList",
		"course:user:add",
		"course:user:del",
		"course:add",
		"course:del",
		"quest:list:read",
		"quest:read",
		"quest:update",
		"quest:create",
		"quest:del",
		"test:quest:del",
		"test:quest:add",
		"test:quest:update",
		"test:answer:read",
		"answer:read",
		"answer:update",
		"answer:del",
	},
}

func PermissionsForRoles(roles []string) []string {
	permSet := make(map[string]struct{})

	for _, role := range roles {
		if perms, ok := RolePermissions[role]; ok {
			for _, p := range perms {
				permSet[p] = struct{}{}
			}
		}
	}

	permissions := make([]string, 0, len(permSet))
	for p := range permSet {
		permissions = append(permissions, p)
	}

	return permissions
}
