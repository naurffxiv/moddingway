package enum

type ExileStatus int

const (
	IndefiniteExile = iota
	TimedExile
	Unknown
)