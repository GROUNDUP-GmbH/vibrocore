//! Modbus RTU register maps.
//!
//! The RevPi is the master. Slave 2 is the SINAMICS S200 PTI.
//! Slave 1 is the sonic-head inverter. Its order code is not selected.
//! A register with `published: None` or `verified_on_device: false` is TODO.
//! Do not send an unverified number to a drive.

/// SINAMICS S200 PTI order code. Part VC-HB-2300.
pub const S200_ORDER_CODE: &str = "6SL5510-1BB11-0AA0";

/// First firmware that documents the S200 PTI Modbus RTU slave.
pub const S200_MODBUS_FIRMWARE: &str = "V6.3 HF4";

/// Modbus RTU slave address of the sonic-head inverter.
pub const SONIC_SLAVE_ID: u8 = 1;

/// Modbus RTU slave address of the S200.
pub const S200_SLAVE_ID: u8 = 2;

/// Modbus RTU slave address of the force ADC. The ADC map is not in this crate.
pub const FORCE_ADC_SLAVE_ID: u8 = 3;

/// One holding register in a device map.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Register {
    pub name: &'static str,
    /// Published holding-register number, when a public example gives one.
    /// This is not a confirmed PDU offset.
    pub published: Option<u16>,
    /// True only after the number is read back on the Vibrocore unit.
    pub verified_on_device: bool,
}

/// One drive parameter from a public example. Not a Modbus address.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct DriveParameter {
    pub name: &'static str,
    pub example_value: i32,
    pub verified_on_device: bool,
}

const S200_REGISTERS: [Register; 6] = [
    Register {
        name: "control_word",
        published: Some(40_100),
        verified_on_device: false,
    },
    Register {
        name: "speed_setpoint",
        published: Some(40_101),
        verified_on_device: false,
    },
    Register {
        name: "status_word",
        published: None,
        verified_on_device: false,
    },
    Register {
        name: "actual_position",
        published: None,
        verified_on_device: false,
    },
    Register {
        name: "actual_speed",
        published: None,
        verified_on_device: false,
    },
    Register {
        name: "actual_torque",
        published: None,
        verified_on_device: false,
    },
];

/// Example values from the public S7-1200 note. Not verified on this drive.
const S200_PARAMETERS: [DriveParameter; 2] = [
    DriveParameter {
        name: "p29008_modbus_control_source",
        example_value: 1,
        verified_on_device: false,
    },
    DriveParameter {
        name: "p29003_speed_mode",
        example_value: 2,
        verified_on_device: false,
    },
];

const SONIC_REGISTERS: [Register; 3] = [
    Register {
        name: "control_word",
        published: None,
        verified_on_device: false,
    },
    Register {
        name: "frequency_setpoint",
        published: None,
        verified_on_device: false,
    },
    Register {
        name: "status_word",
        published: None,
        verified_on_device: false,
    },
];

pub fn s200_registers() -> &'static [Register] {
    &S200_REGISTERS
}

pub fn s200_parameters() -> &'static [DriveParameter] {
    &S200_PARAMETERS
}

pub fn sonic_registers() -> &'static [Register] {
    &SONIC_REGISTERS
}

#[cfg(test)]
mod tests {
    use super::*;

    fn find<'a>(registers: &'a [Register], name: &str) -> &'a Register {
        registers.iter().find(|item| item.name == name).expect(name)
    }

    #[test]
    fn s200_example_registers_stay_unverified() {
        assert_eq!(S200_ORDER_CODE, "6SL5510-1BB11-0AA0");
        assert_eq!(S200_SLAVE_ID, 2);
        assert_eq!(
            find(s200_registers(), "control_word").published,
            Some(40_100)
        );
        assert_eq!(
            find(s200_registers(), "speed_setpoint").published,
            Some(40_101)
        );
        assert!(s200_registers().iter().all(|item| !item.verified_on_device));
        assert_eq!(find(s200_registers(), "actual_position").published, None);
        assert!(s200_parameters()
            .iter()
            .all(|item| !item.verified_on_device));
    }

    #[test]
    fn sonic_map_has_no_published_numbers() {
        assert_eq!(SONIC_SLAVE_ID, 1);
        assert!(sonic_registers()
            .iter()
            .all(|item| item.published.is_none()));
        assert!(sonic_registers()
            .iter()
            .all(|item| !item.verified_on_device));
    }
}
