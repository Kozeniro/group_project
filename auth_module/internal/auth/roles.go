package auth

const (
	RoleUser  = "student"
	RoleAdmin = "admin"
)

var RolePermissions = map[string][]string{
	RoleUser: {
		"profile.read",
	},
	RoleAdmin: {
		"profile.read",
		"profile.write",
		"admin.panel",
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
