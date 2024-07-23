package enum

type ExileStatus int

const (
	Unexiled = iota
	IndefiniteExile
	TimedExile
	Runaway
	Unknown
)