# Thin wrapper over scripts/build.ps1. EP is optional; omitted -> newest episode (test-pipeline: all).
#   make render-video EP=ep02_agent_loops
PS := powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build.ps1
EPARG := $(if $(EP),-Episode $(EP))

.PHONY: setup test-pipeline render-assets render-video
setup test-pipeline render-assets render-video:
	$(PS) $@ $(EPARG)
