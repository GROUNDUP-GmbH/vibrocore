//! Process image for the RevPi DIO.
//!
//! The device node is `/dev/piControl0`. The cyclic service will use `read`,
//! `write` and the ioctls below. Byte offsets come from PiCtory and are not
//! known in this skeleton. Channel numbers are a proposal, not offsets.

use std::fs::File;
use std::io;

/// Kunbus process-image device.
pub const DEVICE_PATH: &str = "/dev/piControl0";

/// Linux `_IO('K', nr)` with a zero size. `K` is `KB_IOC_MAGIC` in `piControl.h`.
pub const fn kb_io(nr: u32) -> u32 {
    (b'K' as u32) << 8 | nr
}

/// `KB_GET_VALUE` in `piControl.h` (`_IO('K', 15)`).
pub const KB_GET_VALUE: u32 = kb_io(15);

/// `KB_SET_VALUE` in `piControl.h` (`_IO('K', 16)`).
pub const KB_SET_VALUE: u32 = kb_io(16);

/// `KB_SET_OUTPUT_WATCHDOG` in `piControl.h` (`_IO('K', 26)`).
///
/// The header says this watchdog sets outputs to 0 when `write` stops.
/// The ioctl argument layout is not confirmed in this crate.
pub const KB_SET_OUTPUT_WATCHDOG: u32 = kb_io(26);

/// One RevPi DIO. These counts are the module rating, not PiCtory offsets.
pub const DIO_INPUTS: u8 = 14;
pub const DIO_OUTPUTS: u8 = 14;

/// Assigned inputs. One input stays spare. A second I/O module is not required.
/// There is no tilt sensor and no analogue module. See `IO-LIST.md`.
pub const DI_ASSIGNED: u8 = 13;
pub const DO_ASSIGNED: u8 = 7;

/// Proposed DIO input index. Not a process-image byte offset.
pub const DI_LIMIT_UP: u8 = 0;
pub const DI_LIMIT_DOWN: u8 = 1;
pub const DI_ESTOP_NC: u8 = 2;
pub const DI_SAFETY_RELAY: u8 = 3;
pub const DI_S200_STO: u8 = 4;
pub const DI_SONIC_STO: u8 = 5;
pub const DI_ENABLING: u8 = 6;
pub const DI_TILT_VERTICAL: u8 = 7;
pub const DI_TILT_FOLDED: u8 = 8;
pub const DI_LIFT_DEPLOYED: u8 = 9;
pub const DI_LIFT_RETRACTED: u8 = 10;
pub const DI_SONIC_FAULT: u8 = 11;
pub const DI_ROTATION_INDEX: u8 = 12;

/// Proposed DIO output index. Not a process-image byte offset.
/// The S200 brake and both STO paths are hard-wired. They are not outputs.
/// The S200 pulse train is not a DIO output.
pub const DO_LIFT_EXTEND: u8 = 0;
pub const DO_LIFT_RETRACT: u8 = 1;
pub const DO_TILT_VERTICAL: u8 = 2;
pub const DO_TILT_FOLD: u8 = 3;
pub const DO_ALARM_BEACON: u8 = 4;
pub const DO_SONIC_RESET: u8 = 5;
pub const DO_ROTATION_ENABLE: u8 = 6;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ImageError {
    Offset,
    /// The output-watchdog ioctl is named, but its argument is not confirmed.
    NotImplemented,
}

/// In-memory process image for tests. This is not `/dev/piControl0`.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MemoryImage {
    bytes: Vec<u8>,
}

impl MemoryImage {
    pub fn new(len: usize) -> Self {
        Self {
            bytes: vec![0; len],
        }
    }

    pub fn len(&self) -> usize {
        self.bytes.len()
    }

    pub fn is_empty(&self) -> bool {
        self.bytes.is_empty()
    }

    pub fn read_byte(&self, offset: usize) -> Option<u8> {
        self.bytes.get(offset).copied()
    }

    pub fn write_byte(&mut self, offset: usize, value: u8) -> Result<(), ImageError> {
        let slot = self.bytes.get_mut(offset).ok_or(ImageError::Offset)?;
        *slot = value;
        Ok(())
    }
}

/// Read one bit. `bit` is 0 to 7. A larger value is rejected.
pub fn read_bit(byte: u8, bit: u8) -> Option<bool> {
    if bit > 7 {
        None
    } else {
        Some(byte & (1 << bit) != 0)
    }
}

/// Open `/dev/piControl0` for read and write.
/// Unit tests do not call this. The image is absent on a development host.
pub fn open_device() -> io::Result<File> {
    File::options().read(true).write(true).open(DEVICE_PATH)
}

/// Copy one process image from the device with `read`.
pub fn read_process_image(file: &mut File, buf: &mut [u8]) -> io::Result<()> {
    use std::io::Read;
    file.read_exact(buf)
}

/// Copy one process image to the device with `write`.
pub fn write_process_image(file: &mut File, buf: &[u8]) -> io::Result<()> {
    use std::io::Write;
    file.write_all(buf)
}

/// Arm `KB_SET_OUTPUT_WATCHDOG`. Not implemented until the argument layout is confirmed.
pub fn set_output_watchdog(_timeout_ms: u32) -> Result<(), ImageError> {
    Err(ImageError::NotImplemented)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ioctl_numbers_match_the_picontrol_header() {
        assert_eq!(DEVICE_PATH, "/dev/piControl0");
        assert_eq!(KB_GET_VALUE, kb_io(15));
        assert_eq!(KB_SET_VALUE, kb_io(16));
        assert_eq!(KB_SET_OUTPUT_WATCHDOG, kb_io(26));
        assert_eq!(set_output_watchdog(10), Err(ImageError::NotImplemented));
    }

    #[test]
    fn memory_image_round_trip_uses_caller_offsets() {
        let mut image = MemoryImage::new(4);
        image.write_byte(1, 0b0000_0100).unwrap();
        assert_eq!(read_bit(image.read_byte(1).unwrap(), 2), Some(true));
        assert_eq!(image.write_byte(9, 1), Err(ImageError::Offset));
        assert_eq!(read_bit(0, 8), None);
    }

    #[test]
    fn discrete_map_fits_one_dio_and_leaves_the_brake_off_the_list() {
        assert_eq!(DIO_INPUTS - DI_ASSIGNED, 1);
        assert_eq!(DIO_OUTPUTS - DO_ASSIGNED, 7);
        assert_eq!(DI_SONIC_FAULT, 11);
        assert_eq!(DI_ROTATION_INDEX, 12);
        assert_eq!(DO_ROTATION_ENABLE, 6);
    }
}
