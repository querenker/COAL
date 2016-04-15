package org.s16a.mcas;

public class MCASException extends Exception {

	private String message;

	public MCASException(String message) {
		this.message = message;
	}

	@Override
	public String getMessage() {
		return message;
	}

}
