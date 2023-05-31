package main

import (
	"fmt"
	"time"

	"github.com/go-audio/audio"
	"github.com/go-audio/audio/mix"
	"github.com/go-audio/wav"
	"github.com/gordonklaus/portaudio"
	"github.com/tebeka/snowboy"
)

const (
	RECORD_TIMEOUT        = 3
	ENERGY_THRESHOLD      = 1000
	DYNAMIC_ENERGY_THRESH = false
)

type BaseRecorder struct {
	Recorder           *snowboy.Recognizer
	Source             *portaudio.Stream
	SourceName         string
}

func NewBaseRecorder(source *portaudio.Stream, sourceName string) *BaseRecorder {
	recorder, err := snowboy.NewRecognizer("resources/common.res")
	if err != nil {
		fmt.Println("Failed to initialize snowboy recognizer:", err)
		return nil
	}

	recorder.SetEnergyThreshold(ENERGY_THRESHOLD)
	recorder.SetDynamicEnergyThreshold(DYNAMIC_ENERGY_THRESH)

	return &BaseRecorder{
		Recorder:   recorder,
		Source:     source,
		SourceName: sourceName,
	}
}

func (r *BaseRecorder) AdjustForNoise(deviceName string, msg string) {
	fmt.Printf("[INFO] Adjusting for ambient noise from %s. %s\n", deviceName, msg)

	if err := r.Source.Start(); err != nil {
		fmt.Println("Failed to start audio source:", err)
		return
	}

	audioBuffer := &audio.IntBuffer{}
	ambientFrames := make([]int, r.Source.Info().SampleRate*5)
	for i := 0; i < len(ambientFrames)/audioBuffer.Format.NumChannels; {
		if err := r.Source.Read(audioBuffer); err != nil {
			fmt.Println("Failed to read audio buffer:", err)
			return
		}
		for _, sample := range audioBuffer.Data {
			ambientFrames[i] = sample
			i++
		}
	}

	if err := r.Recorder.AdjustThreshold(ambientFrames); err != nil {
		fmt.Println("Failed to adjust threshold:", err)
		return
	}

	if err := r.Source.Stop(); err != nil {
		fmt.Println("Failed to stop audio source:", err)
		return
	}

	fmt.Printf("[INFO] Completed ambient noise adjustment for %s.\n", deviceName)
}

func (r *BaseRecorder) RecordIntoQueue(audioQueue chan<- *audio.IntBuffer) {
	callback := func(in []int) {
		audioBuffer := &audio.IntBuffer{
			Data:   in,
			Format: &audio.Format{SampleRate: r.Source.Info().SampleRate, NumChannels: 1},
		}
		audioQueue <- audioBuffer
	}

	if err := r.Source.Start(); err != nil {
		fmt.Println("Failed to start audio source:", err)
		return
	}

	streamParams := r.Source.Info().SampleRate
	if err := r.Recorder.Run(callback, streamParams); err != nil {
		fmt.Println("Failed to run recorder:", err)
		return
	}

	time.Sleep(RECORD_TIMEOUT * time.Second)

	if err := r.Recorder.Stop(); err != nil {
		fmt.Println("Failed to stop recorder:", err)
		return
	}

	if err := r.Source.Stop(); err != nil {
		fmt.Println("Failed to stop audio source:", err)
		return
	}
}

type DefaultMicRecorder struct {
	*BaseRecorder
}

func NewDefaultMicRecorder() *DefaultMicRecorder {
	stream, err := portaudio.OpenDefaultStream(1, 0, 16000, len([]int{0}), nil)
	if err != nil {
		fmt.Println("Failed to open default stream:", err)
		return nil
	}

	return &DefaultMicRecorder{
		BaseRecorder: NewBaseRecorder(stream, "You"),
	}
}

func (r *DefaultMicRecorder) AdjustForNoise() {
	r.BaseRecorder.AdjustForNoise("Default Mic", "Please make some noise from the Default Mic...")
}

type DefaultSpeakerRecorder struct {
	*BaseRecorder
}

func NewDefaultSpeakerRecorder() *DefaultSpeakerRecorder {
	portaudio.Initialize()
	defer portaudio.Terminate()

	wasapiHostAPI := portaudio.HostApis()[portaudio.WASAPI]
	defaultOutputDevice := wasapiHostAPI.Devices[wasapiHostAPI.DefaultOutputDeviceIndex]

	var defaultSpeakers *portaudio.DeviceInfo

	if !defaultOutputDevice.IsLoopbackDevice {
		for _, loopback := range wasapiHostAPI.Devices {
			if loopback.Name == defaultOutputDevice.Name {
				defaultSpeakers = loopback
				break
			}
		}
	}

	if defaultSpeakers == nil {
		fmt.Println("[ERROR] No loopback device found.")
		return nil
	}

	stream, err := portaudio.OpenDefaultStream(0, 1, float64(defaultSpeakers.DefaultSampleRate), defaultSpeakers.MaxInputChannels, nil)
	if err != nil {
		fmt.Println("Failed to open default stream:", err)
		return nil
	}

	return &DefaultSpeakerRecorder{
		BaseRecorder: NewBaseRecorder(stream, "Speaker"),
	}
}

func (r *DefaultSpeakerRecorder) AdjustForNoise() {
	r.BaseRecorder.AdjustForNoise("Default Speaker", "Please make or play some noise from the Default Speaker...")
}

func main() {
	micRecorder := NewDefaultMicRecorder()
	if micRecorder == nil {
		return
	}
	micRecorder.AdjustForNoise()
	audioQueue := make(chan *audio.IntBuffer)
	go micRecorder.RecordIntoQueue(audioQueue)

	speakerRecorder := NewDefaultSpeakerRecorder()
	if speakerRecorder == nil {
		return
	}
	speakerRecorder.AdjustForNoise()
	go speakerRecorder.RecordIntoQueue(audioQueue)

	for audioBuffer := range audioQueue {
		// Process the audio buffer
		fmt.Println("Received audio buffer:", audioBuffer)
	}

	close(audioQueue)
}
