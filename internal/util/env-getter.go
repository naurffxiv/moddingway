package util

import (
	"os"
	"strings"
)

// EnvGetter is a helper that removes the need for error checking
// every single an environment variable is looked up
// instead just moves error checking to the end of the block of code

type EnvGetter struct {
	EnvName string
	Ok      bool
}

func (eg *EnvGetter) GetEnv(envName string) string {
	if !eg.Ok {
		return ""
	}
	eg.EnvName = envName
	var ret string
	ret, eg.Ok = os.LookupEnv(envName)
	ret = strings.TrimSpace(ret)
	return ret
}