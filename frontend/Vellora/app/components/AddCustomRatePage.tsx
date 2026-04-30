import { useState } from "react"
import {
  View,
  Text,
  TextInput,
  Pressable,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  Modal,
  FlatList
} from "react-native"
import { rateStyles } from "../styles/ReimbursementStyles"
import CurrencyInput from "../components/CurrencyInput"

type Category = {
  id: string
  name: string
  rate: string
}

type AddCustomRateProps = {
  onClose?: () => void
  onSave?: (data: {
    name: string
    description: string
    year: string
    categories: Category[]
  }) => void
}

export default function AddCustomRatePage({ onClose, onSave }: AddCustomRateProps) {
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [year, setYear] = useState("")
  const [yearPickerVisible, setYearPickerVisible] = useState(false)

  const [categories, setCategories] = useState<Category[]>([])
  const [newCategoryName, setNewCategoryName] = useState("")
  const [newCategoryRate, setNewCategoryRate] = useState("0.00")
  const [errors, setErrors] = useState("")

  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: currentYear - 1999 + 2 }, (_, i) => `${2000 + i}`)

  const isDuplicateCategory = (name: string) =>
    categories.some((c) => c.name.toLowerCase() === name.toLowerCase())

  const validateBeforeSave = () => {
    if (!name.trim()) return setErrors("Name is required.")
    if (!year.trim()) return setErrors("Year is required.")
    if (categories.length === 0) return setErrors("You must add at least one category.")
    for (const c of categories) {
      if (!c.name.trim()) return setErrors("Category names cannot be empty.")
      if (!c.rate.trim()) return setErrors("Category rates cannot be empty.")
    }
    setErrors("")
    return true
  }

  const handleSave = () => {
    if (!validateBeforeSave()) return
    const payload = { name, description, year, categories }
    if (onSave) onSave(payload)
  }

  const addCategory = () => {
    const trimmed = newCategoryName.trim()
    if (!trimmed) return setErrors("Category name cannot be empty.")
    if (isDuplicateCategory(trimmed)) return setErrors("Category already exists.")

    const newCat: Category = {
      id: `${Date.now()}`,
      name: trimmed,
      rate: newCategoryRate || "0.00"
    }

    setCategories((prev) => [...prev, newCat])
    setNewCategoryName("")
    setNewCategoryRate("0.00")
    setErrors("")
  }

  const updateCategoryRate = (id: string, val: string) => {
    setCategories((prev) =>
      prev.map((c) => (c.id === id ? { ...c, rate: val } : c))
    )
  }

  const deleteCategory = (id: string) => {
    setCategories((prev) => prev.filter((c) => c.id !== id))
  }

  return (
    <SafeAreaView style={rateStyles.safe}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <View style={rateStyles.fullScreenWhite}>
          <View style={rateStyles.formHeaderRow}>
            <Pressable onPress={onClose} style={rateStyles.closeCircle}>
              <Text style={rateStyles.closeText}>×</Text>
            </Pressable>
            <Text style={rateStyles.formTitle}>Add custom rate</Text>
          </View>

          {errors !== "" && (
            <Text style={{ color: "red", marginBottom: 12 }}>{errors}</Text>
          )}

          <View style={rateStyles.formFieldGroup}>
            <Text style={rateStyles.formLabel}>Name</Text>
            <TextInput
              style={rateStyles.formInput}
              value={name}
              onChangeText={setName}
              placeholder="Enter a name for custom rate"
              placeholderTextColor="#9CA3AF"
            />
          </View>

          <View style={rateStyles.formFieldGroup}>
            <Text style={rateStyles.formLabel}>Description</Text>
            <TextInput
              style={rateStyles.formInput}
              value={description}
              onChangeText={setDescription}
              placeholder="Enter a description"
              placeholderTextColor="#9CA3AF"
            />
          </View>

          <View style={rateStyles.formFieldGroup}>
            <Text style={rateStyles.formLabel}>Year</Text>
            <Pressable
              style={[rateStyles.formInput, { width: 120, justifyContent: "center" }]}
              onPress={() => setYearPickerVisible(true)}
            >
              <Text style={{ color: year ? "#000" : "#9CA3AF" }}>
                {year || "Select year"}
              </Text>
            </Pressable>
          </View>

          <Modal visible={yearPickerVisible} transparent animationType="fade">
            <View
              style={{
                flex: 1,
                backgroundColor: "rgba(0,0,0,0.4)",
                justifyContent: "center",
                alignItems: "center"
              }}
            >
              <View
                style={{
                  width: "80%",
                  backgroundColor: "white",
                  borderRadius: 16,
                  padding: 18
                }}
              >
                <Text
                  style={{
                    fontSize: 16,
                    fontWeight: "700",
                    textAlign: "center",
                    marginBottom: 12
                  }}
                >
                  Select Year
                </Text>

                <FlatList
                  data={years}
                  keyExtractor={(item) => item}
                  style={{ maxHeight: 250 }}
                  renderItem={({ item }) => (
                    <Pressable
                      onPress={() => {
                        setYear(item)
                        setYearPickerVisible(false)
                      }}
                      style={{ paddingVertical: 10 }}
                    >
                      <Text style={{ fontSize: 16 }}>{item}</Text>
                    </Pressable>
                  )}
                />

                <Pressable
                  onPress={() => setYearPickerVisible(false)}
                  style={{ marginTop: 10, alignSelf: "center" }}
                >
                  <Text style={{ fontSize: 16, color: "#555" }}>Close</Text>
                </Pressable>
              </View>
            </View>
          </Modal>

          <View style={rateStyles.formHeadingRow}>
            <Text style={rateStyles.sectionLabel}>Categories and costs</Text>
          </View>

          <View style={rateStyles.addRow}>
            <TextInput
              style={rateStyles.categoryInput}
              placeholder="Category name"
              placeholderTextColor="#9CA3AF"
              value={newCategoryName}
              onChangeText={setNewCategoryName}
            />

            <CurrencyInput
              label=""
              value={newCategoryRate}
              onChangeText={setNewCategoryRate}
              style={{ width: 90 }}
            />

            <Pressable onPress={addCategory}>
              <Text style={{ fontSize: 20, color: "green", marginLeft: 12 }}>✓</Text>
            </Pressable>
          </View>

          <View style={rateStyles.divider} />

          {categories.map((c, idx) => (
            <View key={c.id}>
              <View style={rateStyles.rateRow}>
                <Pressable onPress={() => deleteCategory(c.id)}>
                  <View style={rateStyles.minusIcon} />
                </Pressable>
                <Text style={rateStyles.rateRowText}>{c.name}</Text>

                <CurrencyInput
                  label=""
                  value={c.rate}
                  onChangeText={(val) => updateCategoryRate(c.id, val)}
                  style={{ width: 90 }}
                />
              </View>

              {idx < categories.length - 1 && <View style={rateStyles.divider} />}
            </View>
          ))}

          <Pressable onPress={handleSave} style={rateStyles.formSaveButton}>
            <Text style={rateStyles.formSaveText}>Save</Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  )
}
