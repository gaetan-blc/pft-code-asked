// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;



contract SolidityConcepts {

    struct UserProfile {
        string name;
        uint256 age;
        string email;
    }

    // Mapping to store UserProfiles by a unique identifier (address)
    mapping(address => UserProfile) private profiles;

    event ProfileCreated(address indexed user, string name, uint256 age, string email);

    // Function to create a new user profile
    function createProfile(string memory _name, uint256 _age, string memory _email) external {
        // Save the profile in the mapping
        profiles[msg.sender] = UserProfile(_name, _age, _email);
        emit ProfileCreated(msg.sender, _name, _age, _email);
    }

    // Function to retrieve a user's profile
    function getProfile(address _user) external view returns (UserProfile memory) {
        return profiles[_user];
    }

    // Function to update a user's email
    function updateEmail(string memory _newEmail) external {
        require(bytes(profiles[msg.sender].name).length > 0, "Profile does not exist");
        profiles[msg.sender].email = _newEmail;
    }
}
